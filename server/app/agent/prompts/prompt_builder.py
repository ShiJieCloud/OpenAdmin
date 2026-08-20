"""
Prompt 模板管理模块

使用 Jinja2 模板引擎管理 Agent 的系统提示词，支持：
- 动态变量注入（工具列表、用户信息等）
- 条件判断和循环
- 模板与代码分离
- 易于维护和扩展

典型用法：
    ```python
    from app.agent.prompts.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    prompt = builder.render(
        "chat_agent",
        app_name="OpenAdmin",
        tools=agent_tools,
        user=current_user
    )
    ```

@since 2026-08-20
@version 1.0.0
"""

from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader


class PromptBuilder:
    """
    Prompt 模板构建器

    使用 Jinja2 模板引擎渲染系统提示词。
    模板文件存放在 prompts 目录下，扩展名为 .j2。

    Attributes:
        _env: Jinja2 环境实例
        _template_dir: 模板目录路径

    Example:
        ```python
        builder = PromptBuilder()
        prompt = builder.render("chat_agent", tools=[...])
        ```
    """

    def __init__(self, template_dir: str | Path | None = None):
        """
        初始化 Prompt 构建器

        Args:
            template_dir: 模板目录路径（可选，默认为当前目录）
        """
        if template_dir is None:
            template_dir = Path(__file__).parent

        self._template_dir = Path(template_dir)
        self._env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False,
        )

    def render(self, template_name: str, **context: Any) -> str:
        """
        渲染模板

        Args:
            template_name: 模板名称（不含 .j2 扩展名）
            **context: 模板上下文变量

        Returns:
            str: 渲染后的提示词文本

        Raises:
            FileNotFoundError: 模板文件不存在
        """
        template_file = f"{template_name}.j2"
        template = self._env.get_template(template_file)
        return template.render(**context)

    def list_templates(self) -> list[str]:
        """
        列出所有可用模板

        Returns:
            list[str]: 模板名称列表（不含扩展名）
        """
        templates = []
        for f in self._template_dir.glob("*.j2"):
            templates.append(f.stem)
        return sorted(templates)
