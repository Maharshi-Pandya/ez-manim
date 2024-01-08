import os
import logging
import importlib
from typing import Any
from types import ModuleType
import importlib.metadata as importlib_metadata


def check_import(package: str) -> bool:
    """
    Check if a package is available.
    """
    
    try:
        importlib_metadata.version(package)
        return True
    except importlib_metadata.PackageNotFoundError:
        logging.error(
            f"Package {package} not found."
        )
        return False
    

def build_all_paths(structure, current_path: list = None, result: dict = None):
    """
    Recursively build a dictionary of paths from a nested dictionary.
    """

    if result is None:
        result = {}
    if current_path is None:
        current_path = []

    for key, value in structure.items():
        if isinstance(value, dict):
            build_all_paths(value, current_path + [key], result)
        else:
            result[key] = current_path
            for item in value:
                result[item] = current_path + [key]

    return result


def build_top_paths(structure, current_path=None):
    """
    Recursively build a dictionary of all possible paths for given nested dictionary.
    """

    paths = []
    for key, value in structure.items():
        if isinstance(value, dict):
            for sub_path in build_top_paths(value, key):
                paths.append(f'{sub_path}')
        else:
            for item in value:
                paths.append(f'{key}.{item}' if current_path is None else f'{current_path}.{key}.{item}')

    return paths


def get_all_attribues(structure, attrs=None):
    """
    Recursively retreive all names that exist in the nested dictionary.
    """

    if attrs is None:
        attrs = []

    for key, value in structure.items():
        attrs.append(key)
        if isinstance(value, dict):
            get_all_attribues(value, attrs)
        else:
            for item in value:
                attrs.append(item)

    return list(set(attrs))
    

class LazyModule(ModuleType):
    """
    Module class that surfaces all objects but only performs associated imports when the objects are requested.

    Very heavily based by:
    https://github.com/huggingface/diffusers/blob/main/src/diffusers/utils/import_utils.py

    Changes are pointed with a comment
    """

    def __init__(self, name, module_file, import_structure, module_spec=None, extra_objects=None):

        super().__init__(name)
        
        # Create all possible imports
        self._class_to_module = build_all_paths(import_structure)

        # Create all top level modules
        self._modules = set(import_structure.keys())

        # Needed for autocompletion in an IDE
        self.__all__ = get_all_attribues(import_structure)   # create all attributes of given imports
        self.__file__ = module_file
        self.__spec__ = module_spec
        self.__path__ = [os.path.dirname(module_file)]
        self._objects = {} if extra_objects is None else extra_objects
        self._name = name
        self._import_structure = import_structure

    
    def __dir__(self):
        """
        The elements of self.__all__ that are submodules may or may not be in the dir already, depending on whether
        they have been accessed or not. So we only add the elements of self.__all__ that are not already in the dir.

        Needed for autocompletion in an IDE
        """
        
        result = super().__dir__()
        
        for attr in self.__all__:
            if attr not in result:
                result.append(attr)
        return result


    def __getattr__(self, name: str) -> Any:
        """
        Method used when import from.
        """

        if name in self._objects:
            return self._objects[name]
        
        if name in self._modules:
            value = self._get_module(name)
        
        elif name in self._class_to_module.keys():
            # Get the module and then create the whole import path
            _modules = self._class_to_module[name]
            module = self._get_module('.'.join(_modules))
            value = getattr(module, name)
        
        else:
            raise AttributeError(f"module {self.__name__} has no attribute {name}")

        setattr(self, name, value)

        return value


    def _get_module(self, module_name: str):
        """
        Import given module.
        """

        try:
            return importlib.import_module("." + module_name, self.__name__)
        except Exception as e:
            raise RuntimeError(
                f"Failed to import {self.__name__}.{module_name} because of the following error (look up to see its"
                f" traceback):\n{e}"
            ) from e


    def __reduce__(self):
        """
        This method is used to ensure that the LazyModule object can be pickled and unpickled correctly.
        """

        return (self.__class__, (self._name, self.__file__, self._import_structure))
