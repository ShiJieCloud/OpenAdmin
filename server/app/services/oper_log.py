from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import OperLogCRUD
from app.models import OperLog
from app.schemas import OperLogCreateRequest
from app.services.base import BaseService


class OperLogService(BaseService):
    """操作日志服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.oper_log_crud = OperLogCRUD(db_session)

    async def create_oper_log(self, data: OperLogCreateRequest) -> None:
        """
        创建操作日志

        :param data: 操作日志数据
        :return: None
        """
        # 校验参数
        if not data:
            raise BusinessError(RespCodeEnum.PARAM_ERROR, "操作日志数据不能为空")
        
        # 转换为字典
        log_data = data.model_dump()
        await self.oper_log_crud.create_oper_log(log_data) 
