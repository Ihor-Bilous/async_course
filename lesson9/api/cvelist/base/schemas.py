from pydantic import BaseModel, ConfigDict


class BaseParametersObject(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
