import os
import shutil
import subprocess
import zipfile
from pathlib import Path

LAMBDA_BUILD_DIR = Path("lambda_build")
ZIP_FILENAME = "lambda_function.zip"

# Files/folders to include
INCLUDE_FILES = ["ingestion.py", "lambda_function.py", "config.py", "schemas.py", "settings.py"]
INCLUDE_DIRS = ["db", "services"]

# Folders to exclude inside the zip
EXCLUDE_DIR_NAMES = ["__pycache__"]


def clean_build_dir():
    if LAMBDA_BUILD_DIR.exists():
        shutil.rmtree(LAMBDA_BUILD_DIR)
    LAMBDA_BUILD_DIR.mkdir()


def install_dependencies():
    subprocess.run([
        "pip", "install", "-r", "lambda_requirements.txt",
        "-t", str(LAMBDA_BUILD_DIR)
    ], check=True)


def copy_source_files():
    for f in INCLUDE_FILES:
        shutil.copy(f, LAMBDA_BUILD_DIR / f)
    for d in INCLUDE_DIRS:
        shutil.copytree(d, LAMBDA_BUILD_DIR / d, dirs_exist_ok=True)


def create_zip():
    with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(LAMBDA_BUILD_DIR):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]

            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, LAMBDA_BUILD_DIR)
                zipf.write(full_path, relative_path)


if __name__ == "__main__":
    print("🔧 Cleaning build directory...")
    clean_build_dir()

    print("📦 Installing dependencies...")
    install_dependencies()

    print("📁 Copying source files...")
    copy_source_files()

    print("🗜️  Creating zip file...")
    create_zip()

    print(f"✅ Done: {ZIP_FILENAME}")
