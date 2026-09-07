"""openadmin 数据库初始化，包含pgvector向量扩展

Revision ID: 000000000001
Revises:
Create Date: 2026-09-05 17:17:00

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级：创建pgvector扩展，幂等执行，不存在才创建"""
    context = op.get_context()
    context.config.print_stdout("[Migration] 000000000001 -> 开始启用 pgvector 向量扩展")

    # IF NOT EXISTS 保证幂等，重复执行不会报错
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    context.config.print_stdout("[Migration] 000000000001 -> pgvector 向量扩展就绪，已存在则自动跳过")


def downgrade() -> None:
    """
    回滚：不删除pgvector扩展
    警告：DROP EXTENSION vector 会级联删除所有 vector 类型字段，业务数据直接丢失；
    生产环境禁止执行删除扩展操作，此处直接pass。
    如果需要彻底清理，手动在数据库执行 DROP EXTENSION IF EXISTS vector CASCADE;
    """
    context = op.get_context()
    context.config.print_stdout("[Migration] 000000000001 -> 回滚，跳过删除 pgvector 扩展，避免向量数据丢失")
    pass
