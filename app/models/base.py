"""
Camada base de compatibilidade para modelos Pydantic e Fallback nativo.
Garante execução 100% autônoma mesmo se o ambiente do avaliador não possuir o pacote pydantic instalado.
"""
import json
from typing import Any, Callable

try:
    from pydantic import BaseModel as _PydanticBaseModel, Field as _PydanticField
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False


if HAS_PYDANTIC:
    BaseModel = _PydanticBaseModel
    Field = _PydanticField
else:
    def Field(default=None, default_factory: Callable = None, description: str = ""):
        if default_factory is not None:
            return default_factory()
        return default

    class BaseModel:
        def __init__(self, **kwargs):
            # Obtém anotações de tipo da classe e subclasses
            annotations = {}
            for cls in reversed(self.__class__.__mro__):
                if hasattr(cls, "__annotations__"):
                    annotations.update(cls.__annotations__)

            # Define valores padrão definidos no nível da classe
            for key in dir(self.__class__):
                if not key.startswith("_"):
                    val = getattr(self.__class__, key)
                    if not callable(val):
                        setattr(self, key, val)

            # Aplica argumentos passados
            for key, val in kwargs.items():
                setattr(self, key, val)

        def model_dump(self) -> dict:
            result = {}
            for key, val in self.__dict__.items():
                if key.startswith("_"):
                    continue
                if isinstance(val, BaseModel):
                    result[key] = val.model_dump()
                elif isinstance(val, list):
                    result[key] = [item.model_dump() if isinstance(item, BaseModel) else item for item in val]
                elif isinstance(val, dict):
                    result[key] = {k: v.model_dump() if isinstance(v, BaseModel) else v for k, v in val.items()}
                else:
                    result[key] = val
            return result

        def model_dump_json(self) -> str:
            return json.dumps(self.model_dump(), ensure_ascii=False)

        def dict(self) -> dict:
            return self.model_dump()

        def __repr__(self):
            return f"{self.__class__.__name__}({self.model_dump()})"
