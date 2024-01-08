import sys
from typing import TYPE_CHECKING

from .utils.imports import LazyModule


_import_structure = {
    "llm" : {
        "base" : ["BaseLLM"],
        "openai": ["OpenAIManim"]
    },
    "utils" : {
        "imports" : ["check_import", "build_all_paths", "build_top_paths", "get_all_attribues"],
    },
}


if TYPE_CHECKING:

    # Core
    # from .base import Formatter, Core, MetaLLM
    
    pass

else:
    
    sys.modules[__name__] = LazyModule(
        __name__,
        globals()["__file__"],
        _import_structure,
        module_spec=__spec__
    )