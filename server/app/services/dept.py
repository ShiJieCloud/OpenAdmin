from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import DeptCRUD
from app.models import Dept
from app.schemas.dept import DeptCreateRequest, DeptUpdateRequest, DeptInfoResponse
from app.services.base import BaseService


class DeptService(BaseService):
    """部门服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.dept_crud = DeptCRUD(db_session)

    async def get_dept(self, dept_id: int) -> DeptInfoResponse:
        """获取部门详情

        Args:
            dept_id: 部门ID

        Returns:
            DeptInfoResponse: 部门对象

        Raises:
            BusinessError: 部门不存在
        """
        dept = await self.dept_crud.get_dept(dept_id)
        if not dept:
            raise BusinessError(RespCodeEnum.DEPT_NOT_EXIST)
        return DeptInfoResponse.model_validate(dept)

    async def create_dept(self, req: DeptCreateRequest) -> DeptInfoResponse:
        """创建部门

        Args:
            req: 创建部门请求

        Returns:
            DeptInfoResponse: 创建后的部门对象

        Raises:
            BusinessError: 同级部门名称已存在 / 父级部门不存在
        """
        # 校验父级部门是否存在（非顶级部门）
        if req.parent_id > 0:
            parent_dept = await self.dept_crud.get_dept(req.parent_id)
            if not parent_dept:
                raise BusinessError(RespCodeEnum.DEPT_PARENT_NOT_EXIST)

        # 校验同级部门名称是否已存在
        existing_dept = await self.dept_crud.get_dept_by_name(
            dept_name=req.dept_name,
            parent_id=req.parent_id
        )
        if existing_dept:
            raise BusinessError(RespCodeEnum.DEPT_NAME_EXIST)

        dept_data = req.model_dump()
        return await self.dept_crud.create_dept(dept_data)

    async def update_dept(self, req: DeptUpdateRequest) -> DeptInfoResponse:
        """更新部门信息

        Args:
            req: 更新部门请求

        Returns:
            DeptInfoResponse: 更新后的部门对象

        Raises:
            BusinessError: 部门不存在 / 父级部门不存在 / 同级部门名称已存在 / 父级部门不能是自身
        """
        # 校验部门是否存在
        dept = await self.dept_crud.get_dept(req.dept_id)
        if not dept:
            raise BusinessError(RespCodeEnum.DEPT_NOT_EXIST)

        # 校验父级部门不能是自身
        if req.parent_id is not None and req.parent_id == req.dept_id:
            raise BusinessError(RespCodeEnum.DEPT_PARENT_CANNOT_BE_SELF)

        # 校验父级部门是否存在（非顶级部门）
        if req.parent_id is not None and req.parent_id > 0:
            parent_dept = await self.dept_crud.get_dept(req.parent_id)
            if not parent_dept:
                raise BusinessError(RespCodeEnum.DEPT_PARENT_NOT_EXIST)

        # 校验同级部门名称是否已存在
        if req.dept_name and req.dept_name != dept.dept_name:
            parent_id = req.parent_id if req.parent_id is not None else dept.parent_id
            existing_dept = await self.dept_crud.get_dept_by_name(
                dept_name=req.dept_name,
                parent_id=parent_id,
                exclude_id=req.dept_id
            )
            if existing_dept:
                raise BusinessError(RespCodeEnum.DEPT_NAME_EXIST)

        # 构造更新数据：仅包含已赋值的字段（排除主键 dept_id 不参与更新）
        update_data = req.model_dump(exclude_unset=True, exclude={"dept_id"})
        if update_data:
            await self.dept_crud.update_dept(req.dept_id, update_data)
            dept = await self.dept_crud.get_dept(req.dept_id)

        return DeptInfoResponse.model_validate(dept)

    async def delete_dept(self, dept_id: int) -> None:
        """删除部门（物理删除）

        Args:
            dept_id: 部门ID

        Raises:
            BusinessError: 部门不存在 / 部门存在子部门
        """
        dept = await self.dept_crud.get_dept(dept_id)
        if not dept:
            raise BusinessError(RespCodeEnum.DEPT_NOT_EXIST)

        # 校验是否存在子部门
        children_count = await self.dept_crud.count_children(dept_id)
        if children_count > 0:
            raise BusinessError(RespCodeEnum.DEPT_HAS_CHILDREN)

        await self.dept_crud.delete_dept(dept_id)

    async def batch_delete_dept(self, dept_ids: list[int]) -> None:
        """批量删除部门（物理删除）

        Args:
            dept_ids: 部门ID列表

        Raises:
            BusinessError: 部门不存在 / 部门存在子部门
        """
        if not dept_ids:
            return

        # 校验所有部门是否存在
        for dept_id in dept_ids:
            dept = await self.dept_crud.get_dept(dept_id)
            if not dept:
                raise BusinessError(RespCodeEnum.DEPT_NOT_EXIST)

        # 校验所有部门是否存在子部门
        for dept_id in dept_ids:
            children_count = await self.dept_crud.count_children(dept_id)
            if children_count > 0:
                raise BusinessError(RespCodeEnum.DEPT_HAS_CHILDREN)

        await self.dept_crud.batch_delete_dept(dept_ids)

    async def get_dept_list(self) -> list[DeptInfoResponse]:
        """获取部门列表

        Returns:
            list[DeptInfoResponse]: 部门列表
        """
        db_dept_list = await self.dept_crud.get_dept_list()
        dept_list = [DeptInfoResponse.model_validate(dept) for dept in db_dept_list]
        return dept_list
