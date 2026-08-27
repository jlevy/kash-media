import tomllib
from pathlib import Path


def test_extension_wheel_does_not_own_kash_package_initializer() -> None:
    project_root = Path(__file__).parents[1]
    project_config = tomllib.loads((project_root / "pyproject.toml").read_text())
    wheel_excludes = project_config["tool"]["hatch"]["build"]["targets"]["wheel"]["exclude"]

    assert "src/kash/__init__.py" in wheel_excludes
