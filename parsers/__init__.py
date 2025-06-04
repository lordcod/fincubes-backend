from inspect import getmembers
from pathlib import Path
import importlib.util
from parsers.base import IndividualModelBase


def load_dir(dir: Path):
    parsers = {}
    for path in dir.iterdir():
        if path.is_dir():
            parsers.update(load_dir(path))
        if path.name.endswith('.py'):
            spec = importlib.util.spec_from_file_location(
                path.name[:-3], path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _, member in getmembers(module):
                if isinstance(member, type) and issubclass(member, IndividualModelBase) and member is not IndividualModelBase:
                    parsers[member.__model_name__] = member
    return parsers
