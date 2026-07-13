from fastapi import APIRouter, Depends

from app.core.enums import PermCode
from app.core.response import ResponseBuilder, ApiResponse
from app.deps.permission import has_perm
from app.deps.service import get_permission_service
from app.schemas.permission import PermissionResponse
from app.services import PermissionService

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[list[PermissionResponse]],
    dependencies=[Depends(has_perm(PermCode.Perm.READ))],
    summary="获取所有权限列表",
    description="获取系统中所有权限列表（需要具备权限查看权限）"
)
async def get_permission_list(
    permission_service: PermissionService = Depends(get_permission_service)
):
    """
    获取所有权限列表

    权限：`system:perm:read`
    """
    permissions = await permission_service.get_all_permissions()
    perm_list = [PermissionResponse.model_validate(perm) for perm in permissions]
    return ResponseBuilder.success(data=perm_list)
