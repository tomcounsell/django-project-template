import os

output_file = "django-project-template-dump.txt"
exclude_dir = "./env"
file_types = (".py", ".js", ".css", ".html", ".yaml", ".json", ".conf", ".txt")

with open(output_file, "w") as out:
    for root, dirs, files in os.walk("."):
        # Exclude the env directory and its subdirectories
        dirs[:] = [d for d in dirs if os.path.join(root, d) != exclude_dir]

        for file in files:
            if file.endswith(file_types):
                file_path = os.path.join(root, file)
                out.write(f"\n==== {file} ====\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
