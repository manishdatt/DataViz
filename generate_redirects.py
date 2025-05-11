import os
import re
import yaml
import nbformat

print("Python file")
POSTS_DIR = "posts"
REDIRECTS_DIR = "redirects"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SCRIPT_DIR, "posts")
REDIRECTS_DIR = os.path.join(SCRIPT_DIR, "redirects")

os.makedirs(REDIRECTS_DIR, exist_ok=True)

def extract_slug_qmd(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"^---(.*?)---", content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata.get("slug")
        except Exception as e:
            print(f"YAML error in {filepath}: {e}")
    return None

def extract_slug_ipynb(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        if "slug" in nb.metadata:
            return nb.metadata["slug"]

        for cell in nb.cells:
            if "slug" in cell.metadata:
                return cell.metadata["slug"]
    except Exception as e:
        print(f"Skipping invalid notebook: {filepath}")
    return None

for root, dirs, files in os.walk(POSTS_DIR):
    dirs[:] = [d for d in dirs if not d.startswith('.') and 'virtual' not in d and 'checkpoints' not in d]

    for file in files:
        if file.endswith((".qmd", ".ipynb")):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, ".")

            print(f"Processing: {rel_path}")

            if file.endswith(".qmd"):
                slug = extract_slug_qmd(full_path)
            else:
                slug = extract_slug_ipynb(full_path)

            if not slug or not isinstance(slug, str):
                slug = os.path.splitext(file)[0].lower()

            print(f"Using slug for folder: {slug}")

            target_path = rel_path.replace(os.sep, "/")
            target_path = target_path.replace(".ipynb", ".html").replace(".qmd", ".html")

            short_dir = os.path.join(REDIRECTS_DIR, slug)
            os.makedirs(short_dir, exist_ok=True)

            redirect_file = os.path.join(short_dir, "index.html")
            with open(redirect_file, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=/{target_path}">
  <title>Redirecting...</title>
</head>
<body>
  <p>If you are not redirected automatically, <a href="/{target_path}">click here</a>.</p>
</body>
</html>
""")

print("HTML redirect pages generated successfully.")
