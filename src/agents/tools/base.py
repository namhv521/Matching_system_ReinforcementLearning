"""Base Tool decorator ensuring compatibility with both LangChain and direct Python invocations."""

from functools import wraps
from typing import Callable, Any, Dict


class AgentTool:
    """Universal tool wrapper supporting both direct calls and LangChain .invoke()."""

    def __init__(self, func: Callable, name: str = None, description: str = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip()
        self.__doc__ = self.description
        self.__name__ = self.name
        wraps(func)(self)

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def invoke(self, input_data: Any, *args, **kwargs) -> Any:
        if isinstance(input_data, dict):
            return self.func(**input_data)
        if isinstance(input_data, (tuple, list)):
            return self.func(*input_data)
        if input_data is not None:
            return self.func(input_data)
        return self.func(*args, **kwargs)

    def run(self, *args, **kwargs) -> Any:
        return self.__call__(*args, **kwargs)


def tool(func: Callable = None):
    """Decorator to mark a function as an Agent Tool."""
    if func is None:
        return lambda f: AgentTool(f)
    return AgentTool(func)
