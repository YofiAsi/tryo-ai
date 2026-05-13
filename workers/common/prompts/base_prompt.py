from __future__ import annotations

import json
from typing import Any, Generic, Type, TypeVar

from jinja2 import Environment, StrictUndefined
from pydantic import BaseModel, ValidationError


# ---- Jinja env with a robust tojson filter ----
def _tojson(value: Any) -> str:
    # Ensure ascii? set ensure_ascii=False for UTF-8 prompts
    return json.dumps(value, ensure_ascii=False)

JINJA = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
JINJA.filters["tojson"] = _tojson

# ---- Type vars for better editor/type-checker help ----
U = TypeVar("U", bound=BaseModel)
S = TypeVar("S", bound=BaseModel)

class EmptyVars(BaseModel):
    """Empty varset for prompts with no variables."""
    pass

class BasePrompt(Generic[U, S]):
    """
    Static-style prompt base:
      - Subclasses must set: UserVars, SystemVars, user_prompt_template, system_prompt_template
      - Use classmethods to render (no instances needed).
    """

    # Must be overridden by subclasses
    UserVars: Type[U] = EmptyVars  # type: ignore[assignment]
    SystemVars: Type[S] = EmptyVars  # type: ignore[assignment]
    user_prompt_template: str = ""
    system_prompt_template: str = ""

    # Per-subclass caches
    _user_tmpl = None
    _system_tmpl = None

    # Enforce that subclasses set everything correctly at import time
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        # Skip the abstract base itself
        if cls is BasePrompt:
            return
        missing: list[str] = []
        if cls.UserVars is BaseModel:
            missing.append("UserVars")
        if cls.SystemVars is BaseModel:
            missing.append("SystemVars")
        if not cls.user_prompt_template:
            missing.append("user_prompt_template")
        if not cls.system_prompt_template:
            missing.append("system_prompt_template")
        if missing:
            raise TypeError(
                f"{cls.__name__} is missing required definitions: {', '.join(missing)}"
            )

    # ---------- Renderers ----------
    @classmethod
    def render_user(cls, **data: Any) -> str:
        try:
            vars_obj = cls.UserVars(**data)
        except ValidationError as e:
            raise ValueError(f"{cls.__name__}.render_user vars invalid: {e}") from e

        if cls._user_tmpl is None:
            cls._user_tmpl = JINJA.from_string(cls.user_prompt_template)
        return cls._user_tmpl.render(**vars_obj.model_dump())

    @classmethod
    def render_system(cls, **data: Any) -> str:
        try:
            vars_obj = cls.SystemVars(**data)
        except ValidationError as e:
            raise ValueError(f"{cls.__name__}.render_system vars invalid: {e}") from e

        if cls._system_tmpl is None:
            cls._system_tmpl = JINJA.from_string(cls.system_prompt_template)
        return cls._system_tmpl.render(**vars_obj.model_dump())


    # ---------- Schemas (docs/debugging) ----------
    @classmethod
    def user_vars_schema(cls) -> dict[str, Any]:
        schema: dict[str, Any] = cls.UserVars.model_json_schema()
        return schema

    @classmethod
    def system_vars_schema(cls) -> dict[str, Any]:
        schema: dict[str, Any] = cls.SystemVars.model_json_schema()
        return schema
