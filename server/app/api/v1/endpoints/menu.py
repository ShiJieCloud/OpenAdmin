from fastapi import APIRouter, Depends, Body, Path
from app.core.enums import PermCode
from app.core.response import ResponseBuilder, ApiResponse
from app.deps.permission import get_current_active_user, has_perm
from app.deps.service import get_menu_service, get_user_service, get_post_service
from app.models import User
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest, MenuUpdateStatusRequest, MenuResponse, MenuTreeResponse
from app.services import UserService, PostService, MenuService

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


@router.put(
    "/status/{menu_id}",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Menu.UPDATE))],
    summary="更新菜单状态",
    description="更新菜单启用/禁用状态（需具备菜单更新权限）"
)
async def update_menu_status(
    menu_id: int = Path(..., description="菜单ID", gt=0),
    status: int = Body(..., description="状态值：0=启用 1=禁用", ge=0, le=1),
    menu_service: MenuService = Depends(get_menu_service)
):
    """
    更新菜单状态（启用/禁用）

    权限：`system:menu:update`

    **状态说明：**
    - 0：启用状态，菜单可正常访问
    - 1：禁用状态，菜单不可访问（不会出现在用户菜单树中）
    """
    req = MenuUpdateStatusRequest(menu_id=menu_id, status=status)
    await menu_service.update_menu_status(req)
    status_text = "启用" if status == 0 else "禁用"
    return ResponseBuilder.success(message=f"菜单{status_text}成功")


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


@router.get(
    "/tree",
    dependencies=[Depends(has_perm(PermCode.Menu.READ))],
    summary="获取全系统菜单树",
    description="获取所有菜单的完整树结构（管理员查看所有）"
)
async def get_all_menu_tree(
    menu_service: MenuService = Depends(get_menu_service)
):
    """
    获取全系统菜单树（所有菜单，用于菜单管理页面）

    权限：`system:menu:read`
    """
    menus = await menu_service.get_menu_list()
    tree = menu_service._build_menu_tree(menus, 0)
    return ResponseBuilder.success(data=tree)


@router.get(
    "/tree/user",
    response_model=ApiResponse[list[MenuTreeResponse]],
    summary="获取当前用户的权限菜单树",
    description="获取当前登录用户的权限菜单树（前端侧边栏使用）"
)
async def get_user_menu_tree(
    current_user: User = Depends(get_current_active_user),
    menu_service: MenuService = Depends(get_menu_service),
    user_service: UserService = Depends(get_user_service),
    post_service: PostService = Depends(get_post_service),
):
    """
    获取当前用户权限菜单树
    - 超级管理员：返回全部菜单
    - 普通用户：根据角色自动获取权限菜单（自动补全父级目录）
    """
    # 超级管理员直接返回全量菜单
    if current_user.is_superuser:
        menu_tree = await menu_service.get_user_menu_tree([], is_superuser=True)
        return ResponseBuilder.success(data=menu_tree)

    # 1. 获取用户角色 + 岗位角色
    user_roles = await user_service.get_user_roles(current_user.id)
    post_roles = await post_service.get_posts_roles(current_user.id)
    all_roles = user_roles + post_roles

    # 无角色 → 返回空菜单
    if not all_roles:
        return ResponseBuilder.success(data=[])

    # 2. 提取角色编码
    role_codes = [role.role_code for role in all_roles]
    
    # 3. 直接获取菜单树
    menu_tree = await menu_service.get_user_menu_tree(role_codes, is_superuser=False)

    return ResponseBuilder.success(data=menu_tree)
