from datetime import datetime

from pydantic import Field

from cvelist.base.schemas import BaseDTO, BaseParametersObject


class CveDTO(BaseDTO):
    id: str
    title: str
    description: str
    problem_types: str
    published_date: datetime
    updated_date: datetime | None = None
    deleted_date: datetime | None = None


class CveMutationSchemaBase(BaseParametersObject):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=400)
    problem_types: str = Field(min_length=1, max_length=400)


class CreateCveSchema(CveMutationSchemaBase):
    ...


class UpdateCveSchema(CveMutationSchemaBase):
    ...
