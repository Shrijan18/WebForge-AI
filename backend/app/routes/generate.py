from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.graph.workflow import graph
from app.tools.file_tool import FileTool

from app.agents.react_generator import ReactGenerator
from app.agents.review import ReviewAgent

from app.services.template_service import TemplateService

from app.utils.file_parser import parse_files

from app.services.manifest_service import ManifestService
from app.services.project_validator import ProjectValidator
from app.services.image_service import ImageService
from app.config.generation_levels import DEFAULT_GENERATION_LEVEL

router = APIRouter(
    prefix="/api/v1",
    tags=["Website Generator"]
)

file_tool = FileTool()

template_service = TemplateService()
project_validator = ProjectValidator()
review_agent = ReviewAgent()
image_service = ImageService()


class GenerateRequest(BaseModel):
    prompt: str
    generation_level: str = Field(default=DEFAULT_GENERATION_LEVEL)


@router.post("/generate")
def generate(data: GenerateRequest):

    result = graph.invoke(
        {
            "user_prompt": data.prompt,
            "generation_level": data.generation_level,
            "plan": {},
            "frontend": {},
            "backend": {},
            "database": {},
            "review": {}
        }
    )

    plan = result["plan"]
    plan = image_service.enrich_plan(plan)

    generator = ReactGenerator()

    manifest = ManifestService()

    project_name = plan["website_name"].replace(" ", "_")

    project_path = template_service.copy_react_template(project_name)

    batches = manifest.get_batches(plan)
    batch_results = []
    generation_errors = []
    generated_source = {}

    # print(batches)


    print("\n========== GENERATING FILES ==========\n")
    print("\nFiles to Generate:")

    for batch_name, batch_files in batches.items():

        print(f"\n========== GENERATING {batch_name.upper()} ==========\n")

        for file in batch_files:
            print(f"  - {file}")

        try:
            response = generator.generate_batch(
                plan,
                batch_files,
                generated_source
            )

        except Exception as e:
            print(f"Error while generating {batch_name}: {e}")
            batch_results.append({
                "batch": batch_name,
                "status": "failed",
                "expected_files": batch_files,
                "generated_files": [],
                "missing_files": batch_files,
                "error": str(e)
            })
            generation_errors.append(
                f"{batch_name}: generation failed: {e}"
            )
            continue

        print("\n========== GROQ RESPONSE ==========\n")
        print(response)
        print("\n==============================\n")

        if not response.strip():

            print(f"{batch_name} returned an empty response.")
            batch_results.append({
                "batch": batch_name,
                "status": "failed",
                "expected_files": batch_files,
                "generated_files": [],
                "missing_files": batch_files,
                "error": "The model returned an empty response."
            })
            generation_errors.append(
                f"{batch_name}: the model returned an empty response"
            )

            continue

        generated_files = parse_files(response)

        expected_files = set(batch_files)
        actual_files = set(generated_files.keys())

        missing_files = expected_files - actual_files

        if missing_files:

            print(
                f"❌ {batch_name} incomplete."
            )

            print(
                "Missing files:",
                missing_files
            )

            batch_results.append({
                "batch": batch_name,
                "status": "failed",
                "expected_files": batch_files,
                "generated_files": sorted(actual_files),
                "missing_files": sorted(missing_files),
                "error": "The model did not return every requested file."
            })
            generation_errors.append(
                f"{batch_name}: missing files: {', '.join(sorted(missing_files))}"
            )

            continue

        for file_path, content in generated_files.items():
            file_tool.write_file(
                str(project_path / file_path),
                content
            )
            generated_source[file_path] = content

        batch_results.append({
            "batch": batch_name,
            "status": "success",
            "expected_files": batch_files,
            "generated_files": sorted(actual_files),
            "missing_files": []
        })

    print("\n========== DONE ==========\n")



    file_tool.write_json(
        str(project_path.parent / "plan.json"),
        plan
    )

    validation = project_validator.validate(project_path)
    repair_attempts = []

    if validation["status"] != "success" and generated_source:
        repair_files = sorted(generated_source)
        repair_errors = validation["output"][-12000:]

        try:
            repair_response = generator.generate_batch(
                plan,
                repair_files,
                generated_source,
                repair_errors
            )
            repaired_files = parse_files(repair_response)
            missing_repaired_files = set(repair_files) - set(repaired_files)

            if missing_repaired_files:
                repair_attempts.append({
                    "status": "failed",
                    "missing_files": sorted(missing_repaired_files),
                    "error": "The repair response did not return every source file."
                })
            else:
                for file_path, content in repaired_files.items():
                    file_tool.write_file(
                        str(project_path / file_path),
                        content
                    )
                    generated_source[file_path] = content

                validation = project_validator.validate(project_path)
                repair_attempts.append({
                    "status": validation["status"],
                    "validation": validation
                })
        except Exception as error:
            repair_attempts.append({
                "status": "failed",
                "error": str(error)
            })

    if validation["status"] != "success":
        generation_errors.append(
            f"project validation failed during {validation['step']}"
        )

    review = {}

    if generated_source:
        try:
            review = review_agent.review(plan, generated_source)
        except Exception as error:
            review = {
                "score": None,
                "strengths": [],
                "issues": [],
                "summary": "Review could not be completed.",
                "error": str(error)
            }
            generation_errors.append(
                f"review failed: {error}"
            )

    successful_batches = sum(
        batch["status"] == "success"
        for batch in batch_results
    )

    if not generation_errors:
        status = "success"
    elif successful_batches:
        status = "partial"
    else:
        status = "failed"

    return {
        "status": status,
        "project_name": project_name,
        "plan": plan,
        "batches": batch_results,
        "errors": generation_errors,
        "validation": validation,
        "repair_attempts": repair_attempts,
        "review": review
    }