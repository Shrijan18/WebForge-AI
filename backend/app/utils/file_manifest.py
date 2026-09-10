def get_react_files(plan):

    files = [
        "src/App.jsx",
        "src/App.css"
    ]

    # Components
    for component in plan["components"]:
        files.append(f"src/components/{component}.jsx")
        files.append(f"src/components/{component}.css")

    # Pages
    for page in plan["pages"]:
        name = page.replace(" ", "")
        files.append(f"src/pages/{name}.jsx")
        files.append(f"src/pages/{name}.css")

    return files