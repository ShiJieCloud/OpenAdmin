from fastapi import APIRouter, Depends, Body, Path
from app.core.enums.perm_code import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_menu_service
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest, MenuResponse
from app.services.menu import MenuService
from app.core.response import ApiResponse

router = APIRouter()

@router.post(
    "",
    response_model=ApiResponse[MenuResponse],
    dependencies=[Depends(has_perm(PermCode.Menu.CREATE))],
    summary="新增菜单",
    description="新增菜单（需具备菜单创建权限）"
)
async def create_menu(
    req: MenuCreateRequest = Body(..., description="创建菜单请求"),
    menu_service: MenuService = Depends(get_menu_service)
):
    """
    新增菜单，支持层级关联
    """
    menu = await menu_service.create_menu(req)
    menu_info = MenuResponse.model_validate(menu)

    return ResponseBuilder.success(data=menu_info)


@router.put(
    "/{menu_id}",
    response_model=ApiResponse[None],
       dependencies=[Depends(has_perm(PermCode.Menu.UPDATE))],
    summary="编辑菜单",
    description="编辑菜单信息（需具备菜单更新权限）"
)
async def update_menu(
    menu_id: int = Path(..., description="菜单ID", gt=0),
    req: MenuUpdateRequest = Body(..., description="更新菜单请求"),
    menu_service: MenuService = Depends(get_menu_service)
):
    """
    编辑菜单信息
    """
    await menu_service.update_menu(menu_id, req)
    return ResponseBuilder.success(message="更新成功")


@router.delete(
    "/{menu_id}",
    dependencies=[Depends(has_perm(PermCode.Menu.DELETE))],
    summary="删除菜单",
    description="删除菜单（需具备菜单删除权限）"
)
async def delete_menu(
    menu_id: int = Path(..., description="菜单ID", gt=0),
    menu_service: MenuService = Depends(get_menu_service)
):
    """删除菜单

    权限：`system:menu:delete`

    **注意：**
    - 默认情况下，如果菜单有子菜单，删除会失败
    - 设置 recursive=true 可递归删除该菜单及其所有子菜单
    """
    await menu_service.delete_menu(menu_id)
    return ResponseBuilder.success(message="删除成功")


@router.get(
    "/{menu_id}",
    response_model=ApiResponse[MenuResponse],
    dependencies=[Depends(has_perm(PermCode.Menu.READ))],
    summary="获取菜单详情",
    description="获取菜单详情（需具备菜单读取权限）"
)
async def get_menu_detail(
    menu_id: int = Path(..., description="菜单ID", gt=0),
    menu_service: MenuService = Depends(get_menu_service)
):
    """获取菜单详情

    权限：`system:menu:read`
    """
    menu = await menu_service.get_menu(menu_id)
    menu_info = MenuResponse.model_validate(menu)
    return ResponseBuilder.success(
        data=menu_info
    )
