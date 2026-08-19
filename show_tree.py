from pathlib import Path

EXCLUDE = {
    "venv",
    "__pycache__",
    ".git",
    ".idea"
}


def show_tree(path, indent=""):
    for item in sorted(Path(path).iterdir()):
        if item.name in EXCLUDE:
            continue

        print(f"{indent}{item.name}")

        if item.is_dir():
            show_tree(item, indent + "    ")


show_tree(".")