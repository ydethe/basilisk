# build_wheel.py

import platform
import argparse
import os
from pathlib import Path
import zipfile
import shutil

from setuptools import Extension, Distribution
from wheel.cli.convert import convert


def zipdir(path: Path, ziph: zipfile.ZipFile):
    """Add a directory to a zip file

    Args:
        path: Path to the directory to add
        ziph: Opened zip file

    From https://stackoverflow.com/a/1855118

    """
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
            )


def get_basilik_wheel_name() -> str:
    """Get the right wheel name for Basilisk
    Example: Basilisk_Sim-2.2.0b0-cp310-cp310-linux_x86_64.whl

    From https://stackoverflow.com/a/60773383

    Returns:
        The wheel name

    """
    with open("docs/source/bskVersion.txt", "r") as f:
        version = f.read().strip()

    kwargs = dict(
        name="Basilisk_Sim",
        version=version,
        ext_modules=[Extension("stub", sources=[])],
    )

    # create a fake distribution from arguments
    dist = Distribution(attrs=kwargs)

    # finalize bdist_wheel command
    bdist_wheel_cmd = dist.get_command_obj("bdist_wheel")
    bdist_wheel_cmd.ensure_finalized()

    # assemble wheel file name
    distname = bdist_wheel_cmd.wheel_dist_name
    tag = "-".join(bdist_wheel_cmd.get_tag())

    return f"{distname}-{tag}.whl"


def build():
    """Build a wheel file. 3 steps :

    * Determine version strings and file names
    * Build a egg file
    * Build a wheel file

    """
    # ==========================================
    # Determine some constants
    # ==========================================
    # Determine the current python version
    vt = platform.python_version_tuple()
    py_version = ".".join(vt[:-1])

    # Determine Basilisk version
    with open("docs/source/bskVersion.txt", "r") as f:
        version = f.read().strip()

    # Determine wheel and egg file names
    whl_name = get_basilik_wheel_name()
    egg_name = f"Basilisk_Sim-{version}-py{py_version}.egg"

    build_pth = Path("dist3").expanduser().resolve()
    root_pth = Path(os.getcwd()).expanduser().resolve()

    # ==========================================
    # egg file creation
    # ==========================================
    os.chdir(build_pth)

    # Remove former EFF-INFO folder
    shutil.rmtree("EGG-INFO", ignore_errors=True)
    shutil.copytree("Basilisk_Sim.egg-info", "EGG-INFO")

    with zipfile.ZipFile(root_pth / egg_name, "w") as zipf:
        zipdir(Path("EGG-INFO"), zipf)
        zipdir(Path("Basilisk"), zipf)

    shutil.rmtree("EGG-INFO")

    os.chdir(root_pth)

    # ==========================================
    # wheel file creation
    # ==========================================
    convert([egg_name], str(root_pth), False)
    Path(egg_name).unlink()

    for whl in root_pth.glob("*.whl"):
        whl.rename(whl_name)


if __name__ == "__main__":
    build()
