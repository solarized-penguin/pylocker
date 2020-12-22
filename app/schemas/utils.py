import inspect
from typing import Dict, Type, Any

from fastapi import Form
from pydantic import BaseModel


def as_form(cls: Type[BaseModel]) -> Any:
    """
    Adds an 'as_form' class method to decorated methods.
    The 'as_form' method converts pydantic model to form.
    """
    form_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
            annotation=field.outer_type_
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data: Dict[Any, Any]) -> Any:
        return cls(**data)

    signature = inspect.signature(_as_form)
    signature = signature.replace(parameters=form_params)
    _as_form.__signature__ = signature
    setattr(cls, 'as_form', _as_form)

    return cls
