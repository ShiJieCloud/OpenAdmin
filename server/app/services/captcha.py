import base64
import random
import uuid

from app.core.constants import RedisKeyTemplate, TimeSec
from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.core.redis import RedisClient
from app.schemas.auth import CaptchaResponse


class CaptchaService:
    """验证码服务类"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def generate_captcha(self) -> CaptchaResponse:
        """生成验证码图片
        
        Returns:
            CaptchaResponse: 包含验证码ID和图片Base64编码
        """
        # 生成4位验证码
        captcha_code = self._generate_random_code(6)
        
        # 生成唯一标识
        captcha_id = str(uuid.uuid4()).replace("-", "")[:12]
        
        # 生成验证码图片（SVG格式）
        captcha_image = self._generate_captcha_image(captcha_code)
        
        # 存储到Redis，有效期5分钟
        await self.redis_client.set(
            RedisKeyTemplate.captcha(captcha_id),
            captcha_code,
            expire=5 * TimeSec.MINUTE
        )
        
        return CaptchaResponse(
            captcha_id=captcha_id,
            captcha_image=f"data:image/svg+xml;base64,{captcha_image}"
        )

    async def verify_captcha(self, captcha_id: str, captcha_code: str) -> bool:
        """验证验证码是否正确
        
        Args:
            captcha_id: 验证码唯一标识
            captcha_code: 用户输入的验证码
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            BusinessError: 验证码不存在或已过期
            BusinessError: 验证码错误
        """
        # 从Redis获取验证码
        stored_code = await self.redis_client.get(RedisKeyTemplate.captcha(captcha_id))
        
        if stored_code is None:
            raise BusinessError(RespCodeEnum.CAPTCHA_NOT_EXIST)
        
        # 验证验证码（不区分大小写）
        if stored_code.lower() != captcha_code.lower():
            raise BusinessError(RespCodeEnum.CAPTCHA_INVALID)
        
        # 验证成功后删除验证码，防止重复使用
        await self.redis_client.delete(RedisKeyTemplate.captcha(captcha_id))
        
        return True

    def _generate_random_code(self, length: int = 4) -> str:
        """生成随机验证码
        
        Args:
            length: 验证码长度，默认4位
            
        Returns:
            str: 随机验证码字符串
        """
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_captcha_image(self, code: str) -> str:
        """生成验证码 SVG 图片
        
        Args:
            code: 验证码字符串
            
        Returns:
            str: Base64 编码的 SVG 图片
        """
        # 根据验证码长度动态调整图片宽度（6 位验证码需要更宽）
        width = 160
        height = 50
        char_spacing = 22  # 字符间距
        
        # 生成随机颜色
        def random_color():
            r = random.randint(50, 150)
            g = random.randint(50, 150)
            b = random.randint(50, 150)
            return f"rgb({r},{g},{b})"
        
        # 生成字符位置和角度
        chars_data = []
        for i, char in enumerate(code):
            x = 12 + i * char_spacing + random.randint(-2, 2)
            y = 32 + random.randint(-3, 3)
            rotate = random.randint(-15, 15)
            chars_data.append({
                'char': char,
                'x': x,
                'y': y,
                'rotate': rotate,
                'color': random_color(),
                'font_size': random.randint(24, 30)
            })
        
        # 生成干扰线（增加数量）
        lines = []
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            lines.append({
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'color': random_color(),
                'stroke_width': random.randint(1, 2)
            })
        
        # 生成干扰点（增加数量）
        dots = []
        for _ in range(30):
            dots.append({
                'cx': random.randint(0, width),
                'cy': random.randint(0, height),
                'r': random.randint(1, 2),
                'color': random_color()
            })
        
        # 构建 SVG
        svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="background: #f5f5f5;">
            <rect width="100%" height="100%" fill="#f5f5f5"/>
            {''.join(f'<line x1="{l["x1"]}" y1="{l["y1"]}" x2="{l["x2"]}" y2="{l["y2"]}" stroke="{l["color"]}" stroke-width="{l["stroke_width"]}" opacity="0.5"/>' for l in lines)}
            {''.join(f'<circle cx="{d["cx"]}" cy="{d["cy"]}" r="{d["r"]}" fill="{d["color"]}" opacity="0.6"/>' for d in dots)}
            {''.join(f'<text x="{c["x"]}" y="{c["y"]}" font-family="Arial, sans-serif" font-size="{c["font_size"]}" font-weight="bold" fill="{c["color"]}" transform="rotate({c["rotate"]} {c["x"]} {c["y"]})">{c["char"]}</text>' for c in chars_data)}
        </svg>'''
        
        # Base64 编码
        return base64.b64encode(svg_template.encode('utf-8')).decode('utf-8')