from fastapi import APIRouter
from fastapi.params import Depends

from schemas.name import NameIn, NameOut
from cores.agent import generate_name

from cores.auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(prefix="/name", tags=["name"])

@router.post("", response_model=NameOut)
async def create_name(
        data:NameIn,
        user_id: int = Depends(auth_handler.auth_wrapper)
):
    results = await generate_name(data)
    # 注意这里的写法，必须显式告诉schema：这个值是给哪个字段的。
    return NameOut(names=results.names)