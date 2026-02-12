from __future__ import annotations

import os

from Cython.Build import cythonize
from setuptools import setup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
EXCLUDE_DIRS = {
    ".venv",
    ".venv-pypy",
    "venv",
    "build",
    "__pycache__",
    "logs",
}


def collect_sources() -> list[str]:
    sources: list[str] = []

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for filename in files:
            if not filename.endswith(".py"):
                continue
            if filename == "setup.py":
                continue
            sources.append(os.path.join(root, filename))

    core_dir = os.path.join(REPO_ROOT, "core")
    if os.path.isdir(core_dir):
        for root, dirs, files in os.walk(core_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
            for filename in files:
                if filename.endswith(".py"):
                    sources.append(os.path.join(root, filename))

    return sources


setup(
    name="kameleon-agent",
    ext_modules=cythonize(
        collect_sources(),
        compiler_directives={"language_level": "3"},
        build_dir="build",
    ),
    packages=[],
    py_modules=[],
)
