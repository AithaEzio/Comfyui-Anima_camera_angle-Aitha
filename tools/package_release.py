"""Build a clean, reproducible source ZIP without caches or Git metadata."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
NAME = "Comfyui-Anima_camera_angle-Aitha"
VERSION = "1.0.1"


def main():
    files = [ROOT / name for name in (
        "__init__.py", "camera_angle_node.py", "camera_extra_config_node.py", "camera_core.py",
        "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "CHANGELOG.md", "pyproject.toml",
        "package.json", ".gitignore", ".gitattributes",
        "tools/migrate_workflow.py", "tools/package_release.py", "tools/export_preset_reference.py",
    )]
    for directory in ("js", "docs", "examples", "tests"):
        files.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    # Validate the complete manifest before opening the destination.
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
    output = ROOT / "dist" / f"{NAME}-{VERSION}.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            info = ZipInfo(f"{NAME}/{path.relative_to(ROOT).as_posix()}", (2026, 11, 22, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n", encoding="ascii")
    print(f"{output}\nSHA256 {digest}\n{len(files)} files; {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
