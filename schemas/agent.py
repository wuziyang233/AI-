from pydantic import BaseModel, Field
from typing import Annotated, List


class NameSchema(BaseModel):
    # 1 个用法
    name: Annotated[str, Field(..., description="姓名")]
    reference: Annotated[str, Field(..., description="出处")]
    moral: Annotated[str, Field(..., description="寓意")]


class NameResultSchema(BaseModel):
    names: List[NameSchema]
