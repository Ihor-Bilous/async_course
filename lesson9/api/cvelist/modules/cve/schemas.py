from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cvelist.base.schemas import BaseParametersObject


class CveDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    problem_types: str
    reserved_date: datetime | None = None
    published_date: datetime | None = None
    updated_date: datetime | None = None


class CveFilter(BaseModel):
    __allowed_fields = ["reserver_date", "published_date", "updated_date"]

    field: str
    operator: str
    value: Any


class CveListQuery(BaseModel):
    page: int = Field(default=1, description="Page should be greater equal than 1")
    page_size: int = Field(default=20, description="Page size should one of: 20, 50, 100")
    reserved_date_from: datetime | None = None
    published_date_from: datetime | None = None
    updated_date_from: datetime | None = None
    reserved_date_to: datetime | None = None
    published_date_to: datetime | None = None
    updated_date_to: datetime | None = None
    search: str | None = None

    @field_validator("page")
    def validate_page(cls, value: int):
        if value < 1:
            raise ValueError("Page should be greater than or equal to 1")
        return value

    @field_validator("page_size")
    def validate_page_size(cls, value: int):
        if value not in [20, 50, 100]:
            raise ValueError("Page size should be one of: 20, 50, 100")
        return value


class CveMutationSchemaBase(BaseParametersObject):
    id: str
    title: str
    description: str
    problem_types: str
    reserved_date: datetime | None = None
    published_date: datetime | None = None
    updated_date: datetime | None = None


class CreateCveSchema(CveMutationSchemaBase): ...


class UpdateCveSchema(CveMutationSchemaBase): ...
