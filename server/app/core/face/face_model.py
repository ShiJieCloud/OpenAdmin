"""人脸识别模型客户端

封装 insightface buffalo_sc 模型的加载与特征提取：
- 运行时按环境自动选择 onnxruntime 推理后端（CUDA / CoreML / CPU）
- 单例模式加载模型，避免重复初始化 ONNX 会话
- 对外提供图像字节 → 512 维归一化人脸向量的提取能力
"""
from typing import Optional

import cv2
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

from app.config import face_config
from app.core.logger import logger


def _build_onnx_providers() -> list[str]:
    """获取onnxruntime可用推理后端。
    优先级：CUDA(N卡) → CoreML(Apple芯片) → CPU兜底。
    自动过滤本机不支持的后端，消除无效provider警告。
    """
    available = set(ort.get_available_providers())
    preferred = ("CUDAExecutionProvider", "CoreMLExecutionProvider", "CPUExecutionProvider")
    providers = [ep for ep in preferred if ep in available]

    return providers or ["CPUExecutionProvider"]


class FaceModel:
    """人脸识别模型单例封装"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 构建ONNX推理后端（CUDA（N卡） / CoreML（Apple芯片环境） / CPU）
            providers = _build_onnx_providers()
            # 加载人脸模型，自动下载
            cls._instance.app = FaceAnalysis(name=face_config.MODEL_NAME, providers=providers)
            # 有硬件加速用ctx_id=0；纯CPU环境设为‑1（ctx_id<0 时 insightface 会强制使用 CPU）
            ctx_id = -1 if providers == ["CPUExecutionProvider"] else 0
            # 设置检测输入分辨率
            det_size = (face_config.DET_SIZE, face_config.DET_SIZE)
            cls._instance.app.prepare(ctx_id=ctx_id, det_size=det_size)
            cls._instance.providers = providers
            logger.info(
                f"人脸识别模型加载完成，模型: {face_config.MODEL_NAME}，"
                f"det_size: {det_size}，推理后端: {providers}"
            )
        return cls._instance

    def extract_embedding(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        图片二进制提取人脸512维向量（buffalo_sc 识别模型输出维度）
        :param image_bytes: 上传图片bytes
        :return: 512维归一化 ndarray，未检测人脸返回None
        """
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        faces = self.app.get(img)
        if len(faces) == 0:
            return None

        embedding = faces[0].embedding
        # 归一化
        norm = np.linalg.norm(embedding)
        if norm > 1e-6:
            embedding = embedding / norm
        return embedding


# 全局模型单例
face_model = FaceModel()
