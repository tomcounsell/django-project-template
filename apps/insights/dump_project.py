import os

output_file = "project.txt"
exclude_dirs = (
    "./_archive",
    "_docs",
    "./.git",
    "./kubernetes",
    "./.mypy_cache",
    "./staticfiles",
    "./venv",
)
file_types = (
    ".py",
    ".js",
    ".css",
    ".html",
    ".yml",
    ".json",
    ".conf",
    ".txt",
    ".md",
    "Dockerfile",
)

with open(output_file, "w") as out:
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        for file in files:
            if file.endswith(file_types):
                file_path = os.path.join(root, file)
                out.write(f"\n==== {file} ====\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
