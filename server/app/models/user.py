from sqlalchemy import Boolean, String, BigInteger, Integer, DateTime, SMALLINT, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector


from app.models.base import BaseModel


class User(BaseModel):
    """用户模型"""

    __tablename__ = "sys_user"
    __table_args__ = (
        # 人脸向量 HNSW 索引（pgvector 余弦距离 <=> 算子），加速人脸识别登录的最近邻检索
        # 部分索引：仅收录已录入人脸的用户，与人脸检索 SQL 的 face_embedding IS NOT NULL 条件对齐
        Index(
            "ix_sys_user_face_embedding_hnsw",
            "face_embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"face_embedding": "vector_cosine_ops"},
            postgresql_where=text("face_embedding IS NOT NULL"),
        ),
        {"comment": "用户表"},
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="登录账号（唯一）"
    )
    employee_no: Mapped[str | None] = mapped_column(
        String(12),
        nullable=True,
        unique=True,
        index=True,
        comment="工号（唯一）"
    )
    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="登录密码（加密存储）"
    )
    nickname: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="用户昵称/姓名"
    )
    avatar: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="头像URL"
    )
    email: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="邮箱"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="手机号"
    )
    sex: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        comment="性别：0=未知 1=男 2=女"
    )
    status: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        nullable=False,
        comment="账号状态：0=正常 1=禁用 2=锁定 3=注销 4=冻结"
    )
    dept_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="所属部门ID"
    )
    last_login_ip: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="最后登录IP"
    )
    last_login_date: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    login_fail_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="连续登录失败次数"
    )
    lock_time: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="账号锁定时间"
    )
    remark: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="备注"
    )
    del_flag: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        nullable=False,
        comment="删除标志：0=未删除 1=已删除"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否超级管理员"
    )

    # ========== 人脸向量字段（pgvector），未录入人脸为NULL ==========
    face_embedding: Mapped[Vector | None] = mapped_column(
        Vector(512),
        nullable=True,
        comment="人脸512维特征向量，NULL表示未录入人脸"
    )
