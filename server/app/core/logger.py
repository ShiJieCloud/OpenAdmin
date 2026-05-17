from loguru import logger
import logging
import sys
from pathlib import Path
from typing import Optional
from app.config import log_config
from app.core.context import AppContext


class InterceptHandler(logging.Handler):
    """拦截标准 logging 日志到 loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def _get_context_extra(record: dict) -> str:
    """从 AppContext 获取额外的请求上下文信息"""
    try:
        trace_id = AppContext.get_trace_id()
        client_ip = AppContext.get_client_ip()
        request_method = AppContext.get_request_method()
        request_path = AppContext.get_request_path()

        parts = [x for x in [
            f"<yellow>{trace_id}</yellow>" if trace_id else "",
            f"<blue>{client_ip}</blue>" if client_ip else "",
            f"<magenta>{request_method} {request_path}</magenta>" if request_method else "",
        ] if x]

        return " | ".join(parts) + " | " if parts else ""
    except Exception:
        return ""


def _build_log_format(record: dict, base: str) -> str:
    """构建日志格式"""
    extra = _get_context_extra(record)

    log_fmt = base + extra + "{message}"

    if record["exception"]:
        log_fmt += "\n{exception}"

    return log_fmt + "\n"


def _console_format(record) -> str:
    """控制台格式"""
    base = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    )
    return _build_log_format(record, base)


def _file_format(record) -> str:
    """文件格式"""
    base = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
    )
    return _build_log_format(record, base)


class Logger:
    """日志管理器 - 单例模式"""

    _instance: Optional["Logger"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """初始化日志配置"""
        # 清除所有已存在的处理器
        logger.remove()

        # 确保日志目录存在
        log_path = Path(log_config.DIR)
        log_path.mkdir(parents=True, exist_ok=True)

        # 添加控制台输出
        logger.add(
            sys.stdout,
            level=log_config.STDOUT_LEVEL,
            format=_console_format,
            colorize=True,
            enqueue=True,
            backtrace=log_config.BACKTRACE,
            diagnose=log_config.DIAGNOSE,
        )


        # 添加文件输出
        logger.add(
            log_path / "app_{time:YYYY-MM-DD}.log",
            level=log_config.FILE_LEVEL,
            format=_file_format,
            rotation=log_config.ROTATION,
            retention=log_config.RETENTION,
            compression=log_config.COMPRESSION,
            enqueue=True,
            backtrace=log_config.BACKTRACE,
            diagnose=log_config.DIAGNOSE,
        )

        # 添加错误日志单独文件
        logger.add(
            log_path / "error_{time:YYYY-MM-DD}.log",
            level="ERROR",
            format=_file_format,
            rotation=log_config.ROTATION,
            retention=log_config.RETENTION,
            compression=log_config.COMPRESSION,
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        # 拦截第三方库日志
        self._setup_logging_interception()

        self._logger = logger

    def _setup_logging_interception(self) -> None:
        """设置日志拦截，将标准 logging 转向 loguru"""
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        # 拦截常见的第三方库日志
        third_party_loggers = [
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "fastapi",
            "requests",
            "urllib3",
            "asyncio",
        ]

        for logger_name in third_party_loggers:
            log = logging.getLogger(logger_name)
            log.handlers = [InterceptHandler()]
            log.propagate = False

    @property
    def logger(self):
        return self._logger

# 全局导出，方便直接导入使用
logger = Logger().logger