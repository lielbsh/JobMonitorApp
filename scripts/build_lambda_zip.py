import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
LAMBDA_BUILD_ROOT = ROOT_DIR / "lambda_build"
EXCLUDE_DIR_NAMES = ["__pycache__"]

LAMBDA_CONFIGS = {
    "lambda_db": {
        "zip_name": "lambda_db.zip",
        "entry_point": ["lambda_db/lambda_function.py", "lambda_db/settings.py"],
        "requirements": "lambda_db/requirements.txt",
        "include_dirs": ["db"],
    },
    "lambda_analyze_email": {
        "zip_name": "lambda_analyze_email.zip",
        "entry_point": ["lambda_analyze_email/lambda_function.py", "lambda_analyze_email/settings.py"],
        "requirements": "lambda_analyze_email/requirements.txt",
        "include_files": ["config.py", "schemas.py"],
        "include_dirs": ["services"],
    }
}


def clean_build_dir():
    if LAMBDA_BUILD_ROOT.exists():
        shutil.rmtree(LAMBDA_BUILD_ROOT)
    LAMBDA_BUILD_ROOT.mkdir()


def install_dependencies(requirements_file: str, build_path: Path, use_docker: bool = True):
    if not Path(requirements_file).exists():
        print(f"⚠️  Skipping dependency install: {requirements_file} not found")
        return

    if use_docker:
        print("🐳 Installing in Amazon Linux Docker container...")
        # build_path_relative = str(build_path.relative_to(ROOT_DIR))  # אל תשתמשי בזה
        build_path_in_container = "/var/task/" + str(build_path.relative_to(ROOT_DIR)).replace("\\", "/")
        
        subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{ROOT_DIR}:/var/task",
            "-w", "/var/task",
            "amazonlinux:2",
            "bash", "-c",
            f"""
            yum install -y python3 python3-pip zip &&
            pip3 install --upgrade pip &&
            pip3 install -r {requirements_file} -t {build_path_in_container}
            """
        ], check=True)
    else:
        subprocess.run([
            "pip", "install", "-r", requirements_file,
            "-t", str(build_path)
        ], check=True)




def copy_source_files(config: dict, build_path: Path):
    entry_points = config.get("entry_point", [])
    if isinstance(entry_points, str):
        entry_points = [entry_points]

    for entry_path in entry_points:
        src = ROOT_DIR / entry_path
        dst = build_path / Path(entry_path).name 
        if not src.exists():
            print(f"⚠️  Skipping missing entry point: {src}")
            continue
        shutil.copy(src, dst)

    for f in config.get("include_files", []):
        shutil.copy(ROOT_DIR / f, build_path / f)

    for d in config.get("include_dirs", []):
        shutil.copytree(ROOT_DIR / d, build_path / d, dirs_exist_ok=True)



def create_zip(build_path: Path, output_zip: str):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, build_path)
                zipf.write(full_path, relative_path)


def build_lambda(lambda_name: str, config: dict):
    print(f"\n🚀 Building: {lambda_name}")
    build_path = LAMBDA_BUILD_ROOT / lambda_name
    build_path.mkdir(parents=True)

    print("📦 Installing dependencies...")
    install_dependencies(config["requirements"], build_path)

    print("📁 Copying source files...")
    copy_source_files(config, build_path)

    print("🗜️  Creating zip...")
    create_zip(build_path, config["zip_name"])

    print(f"✅ Done: {config['zip_name']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    clean_build_dir()

    if args:
        for lambda_name in args:
            if lambda_name not in LAMBDA_CONFIGS:
                print(f"❌ Unknown lambda: {lambda_name}")
            else:
                build_lambda(lambda_name, LAMBDA_CONFIGS[lambda_name])
    else:
        for lambda_name, config in LAMBDA_CONFIGS.items():
            build_lambda(lambda_name, config)
