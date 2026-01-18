from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ResponseOut(BaseModel):
    result: Annotated[Literal["success", "failure"], Field("success", description="操作的结果")]