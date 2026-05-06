from typing import Callable, Awaitable
from fastapi import Depends

from app.core.enums import RespCodeEnum
from app.core.exceptions import PermDeniedException
from app.deps.auth import get_current_active_user
from app.deps.service import get_user_service, get_permission_service
from app.models import User
from app.services import UserService, PermissionService


async def get_current_user_roles(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> list[str]:
    """
    获取当前用户的角色列表
    """
    # 超级管理员返回空列表，由 __call__ 统一处理
    if current_user.is_superuser:
        return ["*"]

    user_roles = await user_service.get_user_roles(current_user.id)

    # 提取角色编码
    return [r.role_code for r in user_roles]


async def get_current_user_perms(
    current_user: User = Depends(get_current_active_user),
    user_roles: list[str] = Depends(get_current_user_roles),
    perm_service: PermissionService = Depends(get_permission_service)
) -> list[str]:
    """
    获取当前用户的权限列表
    """
    # 超级管理员通配符
    if current_user.is_superuser:
        return ["*"]

    # 提取角色编码
    if not user_roles:
        return []

    # 根据角色ID批量查询权限编码
    perms = await perm_service.get_perms_by_role_codes(user_roles)
    
    # 提取权限编码
    return [p.perm_code for p in perms]


class PermChecker:
    """
    可链式组合的权限校验器
    用于将单个权限/角色校验逻辑封装为对象，支持 AND/OR 链式组合
    """

    def __init__(self, check: Callable[[list[str], list[str]], Awaitable[None]]):
        self.check = check

    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        role_codes: list[str] = Depends(get_current_user_roles),
        perm_codes: list[str] = Depends(get_current_user_perms)
    ):
        # 超级管理员直接放行（统一入口）
        if current_user.is_superuser:
            return

        await self.check(role_codes, perm_codes)

    def and_(self, other: "PermChecker") -> "PermChecker":
        """
        链式 AND 组合：当前校验 与 另一个校验必须同时通过
        短路规则：前一个校验失败，后一个不再执行
        """
        async def combined(role_codes: list[str], perm_codes: list[str]):
            await self.check(role_codes, perm_codes)
            await other.check(role_codes, perm_codes)
        return PermChecker(combined)

    def or_(self, other: "PermChecker") -> "PermChecker":
        """
        链式 OR 组合：当前校验 或 另一个校验通过一个即可
        短路规则：前一个校验通过，后一个不再执行
        """
        async def combined(role_codes: list[str], perm_codes: list[str]):
            try:
                await self.check(role_codes, perm_codes)
            except PermDeniedException:
                await other.check(role_codes, perm_codes)
        return PermChecker(combined)

    def __and__(self, other: "PermChecker") -> "PermChecker":
        return self.and_(other)

    def __or__(self, other: "PermChecker") -> "PermChecker":
        return self.or_(other)


def has_perm(*perms: str) -> PermChecker:
    """
    必须同时拥有所有权限（AND 逻辑）
    """
    required = set(perms)
    async def check(role_codes: list[str], perm_codes: list[str]):
        if not required.issubset(perm_codes):
            # 打印【权限不足】告警日志（重要！用于排查问题）
            print(
                f"[权限不足] 拒绝访问 | "
                f"缺少权限: {required - set(perm_codes)} | "
                f"用户权限: {perm_codes} | "
                f"接口要求权限: {required}"
            )

            raise PermDeniedException(RespCodeEnum.PERM_DENIED)
        # 校验通过日志（可选）
        print("[权限校验通过] 允许访问"
            f"用户权限: {perm_codes} | "
            f"接口需要权限: {required}"
        )
    return PermChecker(check)


def has_any_perm(*perms: str) -> PermChecker:
    """
    只需拥有任意一个权限（OR 逻辑）
    """
    required = set(perms)   
    async def check(role_codes: list[str], perm_codes: list[str]):
        if not required & set(perm_codes):
            # 打印【权限不足】告警日志（重要！用于排查问题）
            print(
                f"[权限不足] 拒绝访问 | "
                f"缺少权限: {required - set(perm_codes)} | "
                f"用户权限: {perm_codes} | "
                f"接口要求权限: {required}"
            )
            
            raise PermDeniedException(RespCodeEnum.PERM_DENIED)
        # 校验通过日志（可选）
        print("[权限校验通过] 允许访问"
            f"用户权限: {perm_codes} | "
            f"接口需要权限: {required}"
        )
    return PermChecker(check)


def has_role(*roles: str) -> PermChecker:
    """
    必须同时拥有所有角色（AND 逻辑）
    """
    required = set(roles)
    async def check(role_codes: list[str], perm_codes: list[str]):
        if not required.issubset(role_codes):
            # 打印【角色不足】告警日志（重要！用于排查问题）
            print(
                f"[角色不足] 拒绝访问 | "
                f"缺少角色: {required - set(role_codes)} | "
                f"用户角色: {role_codes} | "
                f"接口要求角色: {required}"
            )
            raise PermDeniedException(RespCodeEnum.PERM_DENIED)
        # 校验通过日志（可选）
        print("[角色校验通过] 允许访问"
            f"用户角色: {role_codes} | "
            f"接口需要角色: {required}"
        )
            
    return PermChecker(check)


def has_any_role(*roles: str) -> PermChecker:
    """
    拥有任意一个角色即可（OR 逻辑）
    :param roles: 角色编码列表
    """
    required = set(roles)
    async def check(role_codes: list[str], perm_codes: list[str]):
        if not required & set(role_codes):
            # 打印【角色不足】告警日志（重要！用于排查问题）
            print(
                f"[角色不足] 拒绝访问 | "
                f"缺少角色: {required - set(role_codes)} | "
                f"用户角色: {role_codes} | "
                f"接口要求角色: {required}"
            )
            raise PermDeniedException(RespCodeEnum.PERM_DENIED)
        # 校验通过日志（可选）
        print("[角色校验通过] 允许访问"
            f"用户角色: {role_codes} | "
            f"接口需要角色: {required}"
        )
    return PermChecker(check)
