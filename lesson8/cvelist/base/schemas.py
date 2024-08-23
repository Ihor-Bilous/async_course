from typing import Self

from pydantic import BaseModel, ConfigDict

from cvelist.orm.models import Base


class BaseParametersObject(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class BaseDTO(BaseModel):
    @classmethod
    def from_model_to_dto(cls, model_instance: Base) -> Self:
        return cls(
            **{
                column.key: getattr(model_instance, column.key)
                for column in model_instance.__table__.columns
            }
        )
