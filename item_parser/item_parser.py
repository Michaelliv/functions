from dataclasses import asdict, dataclass, field
from os import listdir
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator

from mlrun import import_function
import yaml


@dataclass
class Function:
    filename: str = ""
    handler: str = ""
    requierments: List[str] = field(default_factory=list)
    kind: str = ""
    image: str = ""


@dataclass
class Maintainer:
    name: str = ""
    email: str = ""


@dataclass
class Item:
    api_version: str = "v1"
    name: str = ""
    version: str = ""
    mlrun_version: str = ""
    platform_version: str = ""
    description: str = ""
    doc: str = ""
    example: str = ""
    icon: str = ""
    url: str = ""
    categories: List[str] = field(default_factory=list)
    labels: Dict[str, Union[str, int, float]] = field(default_factory=dict)
    function: Function = field(default_factory=Function)
    maintainers: List[Maintainer] = field(default_factory=list)


def snake_case_to_lower_camel_case(string: str) -> str:
    if "_" not in string:
        return string
    else:
        components = string.split("_")
        return components[0] + "".join(c.title() for c in components[1:])


def locate_py_file(dir_path: Path) -> Optional[str]:
    default_py_file = dir_path / "function.py"

    if default_py_file.exists:
        return "function.py"

    py_file = list(filter(lambda d: d.suffix == ".py", dir_path.iterdir()))

    if len(py_file) > 1:
        raise RuntimeError(
            "Failed to infer business logic python file name, found multiple python files"
        )
    elif len(py_file) == 1:
        return py_file[0].name

    return None


def iter_relevat_directories(root_path: Path) -> Generator[Path, None, None]:
    for dir in root_path.iterdir():
        if not dir.is_dir():
            continue

        if dir.name.startswith("."):
            continue

        if not (dir / "function.yaml").exists():
            continue

        yield dir


def function_to_item(function_yaml: Path) -> Item:
    model = import_function(str(function_yaml.absolute()))
    item = Item(
        name=model.metadata.name or "",
        version=model.metadata.tag or "",
        mlrun_version="",
        platform_version="",
        description=model.spec.description or "",
        doc="",
        example="",
        icon="",
        url="",
        categories=model.metadata.categories or [],
        labels=model.metadata.labels or {},
        function=Function(
            filename=locate_py_file(function_yaml.parent) or "",
            handler=model.spec.default_handler,
            requierments=[],
            kind=model.kind,
            image=model.spec.build.base_image,
        ),
        maintainers=[],
    )
    return item


def process_item(function_yaml: Path) -> dict:
    item = function_to_item(function_yaml)
    item = {snake_case_to_lower_camel_case(k): v for k, v in asdict(item).items()}
    return item


if __name__ == "__main__":
    root = Path(".").parent.parent.absolute()
    for dir in iter_relevat_directories(root):
        item = process_item(dir / "function.yaml")
        with open(dir / "item.yaml", "w") as f:
            yaml.dump(item, f)
