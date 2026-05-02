from fastapi import APIRouter, Depends, Path

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_user_service
from app.schemas.base.response import ApiResponse
from app.schemas.user import UserInfoResponse
from app.services.user import UserService

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.READ))],
    summary="获取用户详情",
    description="根据用户唯一ID查询指定用户的详细信息（需要具备用户查看权限）"
)
async def get_user_info(
    user_id: int = Path(..., description="用户ID", ge=1, example=1001),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取用户详情
    
    根据用户ID查询用户完整信息，包括基础信息、状态等，
    接口需要用户登录并拥有用户查看权限方可访问。
    
    :param user_id: 目标用户的唯一标识ID
    :return: 返回用户详细信息
    :raises BusinessError: 用户不存在
    """
    user = await user_service.get_user(user_id)
    user_info = UserInfoResponse.model_validate(user)
    return ResponseBuilder.success(user_info)
