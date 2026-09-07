"""人脸识别基础设施包

对外暴露人脸模型单例与相似度阈值，业务层通过：
    from app.core.face import face_model, FACE_SIMILARITY_THRESHOLD
"""
from app.core.face.face_model import FaceModel, face_model

__all__ = ["FaceModel", "face_model"]
