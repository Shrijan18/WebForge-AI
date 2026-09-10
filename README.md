# WebForge AI

WebForge AI turns a natural-language website brief into a runnable React website. It creates a structured plan, selects a generation level, enriches image requirements with Unsplash, generates source files, validates the generated project, attempts one repair pass when needed, and exposes the result through the WebForge dashboard.

## Current Workflow

```text
User prompt + generation level
        |
        v
FastAPI POST /api/v1/generate
        |
        v
LangGraph planner
  - website identity
  - pages and components
  - content strategy
  - design system
  - image asset briefs
        |
        v
Generation level normalization
  - Basic: 2-3 pages/components
  - Intermediate: 4-5 pages/components (default)
  - Advanced: 6-7 pages/components
        |
        v
Unsplash image enrichment
  - searches planned image queries
  - adds stable image URLs and attribution
  - uses a verified fallback catalog when needed
        |
        v
React file generation in batches
  - layout and global CSS
  - shared components
  - pages
        |
        v
Generated project validation
  - npm install
  - npm run build
        |
        +--> one bounded repair attempt when validation fails
        |
        v
LLM code review
  - score
  - strengths
  - actionable issues
        |
        v
API response shown in the WebForge dashboard
```

The LangGraph workflow currently owns the planning step. File generation, image enrichment, validation, repair, and review are coordinated by the generation route after the plan is returned.

## Features

- Natural-language website planning
- Three generation levels:
  - **Basic:** 2-3 pages and components with focused content
  - **Intermediate:** 4-5 pages and components with moderate detail
  - **Advanced:** 6-7 pages and components with richer content
- Intermediate is selected by default
- Structured design-system planning
- Real-world image search through the Unsplash API
- Verified fallback image catalog
- Photographer and Unsplash attribution metadata
- Batch React and CSS file generation
- Generated project build validation
- One automatic repair pass for build failures
- Generated-source quality review
- Generated project history
- Start generated projects from the dashboard

## Project Structure

```text
WebForge-AI/
├── backend/
│   ├── app/
│   │   ├── agents/             Planner, React generator, reviewer
│   │   ├── config/             Settings and generation levels
│   │   ├── graph/              LangGraph planning workflow
│   │   ├── prompts/            Planner and React generation prompts
│   │   ├── routes/             Generate, run, and project history APIs
│   │   ├── services/           Images, templates, validation, history, runner
│   │   ├── schemas/            Website plan models
│   │   └── utils/              Parsers and file helpers
│   ├── requirements.txt
│   └── .env                    Local secrets, not committed
├── frontend/
│   ├── src/
│   │   ├── App.jsx             Generator dashboard
│   │   └── pages/History.jsx   Generated project history
│   └── package.json
├── generated_projects/         Generated output, ignored by Git
└── README.md
```

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer
- npm
- A Groq API key
- An Unsplash developer access key for live image search

## Configuration

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-20b
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
```

The backend reads these values through `python-dotenv`. Never expose either key in the frontend or generated projects.

`GROQ_MODEL` is configurable. The current default is `openai/gpt-oss-20b`; use a model available to your Groq account and monitor its request and token limits.

## Installation

### Backend

From the repository root on Windows PowerShell:

```powershell
cd backend
python -m venv ..\\.venv
..\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

From Git Bash:

```bash
cd backend
python -m venv ../.venv
source ../.venv/Scripts/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running WebForge AI

Start the backend in one terminal:

```bash
cd backend
uvicorn app.main:app --reload
```

Start the dashboard in another terminal:

```bash
cd frontend
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Backend welcome response |
| GET | `/health` | Health check |
| POST | `/api/v1/generate` | Plan and generate a website |
| GET | `/api/v1/projects` | List generated projects |
| POST | `/api/v1/run` | Start a generated project |
| POST | `/api/v1/projects/{project_name}/run` | Start a project from history |

### Generate request

```json
{
  "prompt": "A premium coffee roaster website for remote workers",
  "generation_level": "intermediate"
}
```

Valid levels are `basic`, `intermediate`, and `advanced`. If omitted or invalid, the backend uses `intermediate`.

### Generate response shape

The response includes:

- `status`: `success`, `partial`, or `failed`
- `project_name`
- `plan`
- `batches`
- `errors`
- `validation`
- `repair_attempts`
- `review`

## Generated Projects

Generated websites are written to:

```text
generated_projects/<ProjectName>/frontend/
```

Each generated project contains its own Vite app. To run one manually:

```bash
cd generated_projects/<ProjectName>/frontend
npm install
npm run dev
```

The backend runner can start the project through the dashboard or the run API.

## Image Generation Workflow

The planner creates image asset briefs containing a purpose, subject, search query, and alt text. The backend then calls Unsplash using `UNSPLASH_ACCESS_KEY` and passes the selected image URL and attribution metadata into the React generator.

If Unsplash is unavailable, rate-limited, or returns no result, WebForge AI uses a verified fallback catalog. Generated image implementations should include responsive sizing, meaningful `alt` text, and attribution when metadata is available.

## Performance Improvement Plan

### Priority 1: Make generation asynchronous

The `/generate` request currently performs all model calls, Unsplash searches, file writes, npm installation, build validation, repair, and review before returning. Move this work to a background job system and return a job ID immediately.

Recommended flow:

```text
POST /generate -> job_id
GET /jobs/{job_id} -> progress and current stage
GET /jobs/{job_id}/result -> final result
```

This prevents request timeouts and keeps the dashboard responsive.

### Priority 2: Cache repeated work

Add caching for:

- Planner results keyed by normalized prompt and generation level
- Unsplash searches keyed by query
- Dependency installation per template lockfile
- Validation results keyed by project source hash
- Review results keyed by source hash

A small SQLite or Redis cache would reduce both latency and API usage.

### Priority 3: Reduce model calls

Current generation makes one LLM request per batch, then may make a full repair request and a full review request. Improve this by:

- Generating related page files together when the level allows it
- Sending only the minimum relevant context
- Skipping review when the build fails
- Reviewing changed files after repair instead of the entire project
- Using deterministic checks before asking the model to repair

### Priority 4: Avoid repeated `npm install`

The validator currently runs `npm install` before every generated-project build. Use a shared dependency cache or copy a prepared `node_modules` strategy where appropriate. At minimum, skip installation when `package-lock.json` and `node_modules` already match.

### Priority 5: Move blocking work out of FastAPI request handlers

The generate route uses synchronous model calls and subprocesses. Run blocking work through a background worker or an executor. Also add explicit subprocess timeouts and capture structured logs instead of printing full model responses.

### Priority 6: Parallelize independent work carefully

After the plan is fixed:

- Independent Unsplash queries can run concurrently with a small limit.
- Component batches that do not depend on one another can be grouped or generated concurrently.
- Validation must remain after all files are written.

Use bounded concurrency to avoid Groq and Unsplash rate limits.

### Priority 7: Add observability

Track per generation:

- Planner latency
- Image search latency and cache hit rate
- Tokens requested and used
- Batch generation latency
- Build duration
- Repair count
- Review duration
- Total generation duration

This will show whether latency is caused by the model, image API, npm, or validation.

### Priority 8: Improve reliability controls

Add:

- Request size limits
- Prompt normalization
- Retries with exponential backoff for transient API errors
- Circuit breaking for repeated Unsplash failures
- Per-job cancellation
- Cleanup for abandoned generated projects
- A maximum total generation time

## Testing and Validation

Frontend build:

```bash
cd frontend
npm run build
npm run lint
```

Backend syntax check:

```bash
cd backend
python -m py_compile app/main.py app/routes/generate.py app/services/image_service.py
```

Generated project build:

```bash
cd generated_projects/<ProjectName>/frontend
npm install
npm run build
```

## Troubleshooting

### Groq token-limit errors

Use a model available under your Groq account limits, lower the completion budget, reduce generation level, or retry later. The generator already uses compact context and a bounded fallback request.

### Unsplash images do not load

Check that `UNSPLASH_ACCESS_KEY` is present in `backend/.env`, restart Uvicorn after changing it, and verify the backend can reach `https://api.unsplash.com`. The fallback catalog is used when search fails.

### CORS errors

The backend currently allows the Vite origin `http://localhost:5173`. If Vite runs on another port, update the CORS configuration in `backend/app/main.py`.

### Generated project fails to build

Inspect the `validation`, `errors`, and `repair_attempts` fields in the generate response. Run `npm install` and `npm run build` inside the generated project's frontend directory for the complete Vite error.

## Security Notes

- Keep `.env` files out of Git.
- Keep Groq and Unsplash keys on the backend.
- Do not include API keys in generated source files.
- Validate generated file paths before writing them to disk.
- Treat generated code and model output as untrusted input.
