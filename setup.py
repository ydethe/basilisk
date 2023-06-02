import toml
from setuptools import Extension, setup


class CMakeExtension(Extension):
    """
    An extension to run the cmake build

    This simply overrides the base extension class so that setuptools
    doesn't try to build your sources for you
    """

    def __init__(self):
        with open("pyproject.toml", "r") as f:
            cfg = toml.load(f)
        super().__init__(name=cfg["project"]["name"], sources=[])


if __name__ == "__main__":
    setup(
        ext_modules=[CMakeExtension()],
    )
