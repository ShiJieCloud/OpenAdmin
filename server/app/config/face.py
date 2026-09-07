from app.config.base import BaseConfig
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class FaceConfig(BaseConfig):
    """人脸识别相关配置（insightface 模型加载与比对阈值）

    InsightFace模型选型：
    buffalo_l:  326MB,128维｜服务端首选，精度高，CPU可用
    buffalo_m:  313MB,128维｜速度略快，精度接近 buffalo_l
    buffalo_s:  159MB,128维｜轻量，小内存服务器/边缘，精度小幅下降
    buffalo_sc: 16MB, 128维｜超小体积，嵌入式，精度下降明显
    antelopev2: 407MB,512维｜精度最高，需手动下载；pgvector字段改为Vector(512)

    ⚠️ 切换模型务必同步修改pgvector向量字段维度，入库与检索embedding维度必须一致。
    ⚠️ 仅执行人脸特征比对（无活体防护），静态照片可冒充登录。
    """

    MODEL_NAME: str = Field(
        default="buffalo_sc",
        description="insightface 模型包名称"
    )
    DET_SIZE: int = Field(
        default=640,
        ge=320,
        le=1280,
        description="人脸检测输入尺寸（正方形边长），CPU 推理性能不足可调小为 320"
    )
    SIMILARITY_THRESHOLD: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="人脸比对余弦相似度阈值，1-余弦距离 >= 该值判定为同一人"
    )

    model_config = SettingsConfigDict(
        env_prefix="FACE_"
    )


face_config = FaceConfig()
