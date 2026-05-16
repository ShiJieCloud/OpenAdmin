from pydantic import BaseModel, Field


class IPLocationInfo(BaseModel):
    """IP归属地信息"""
    client_ip: str | None = Field(None, description="IP地址")
    ip_country: str | None = Field(None, description="国家")
    ip_province: str | None = Field(None, description="省份")
    ip_city: str | None = Field(None, description="城市")

    @property
    def full_location(self) -> str:
        """获取完整归属地字符串
        
        拼接规则：
        - 国家 + 省份 + 城市
        - 分隔符：地域用 '-'
        """
        # 构建地域部分
        location_parts = []
        
        # 添加国家
        if self.ip_country:
            location_parts.append(self.ip_country)
        
        # 添加省份
        if self.ip_province:
            location_parts.append(self.ip_province)
        
        # 添加城市
        if self.ip_city:
            location_parts.append(self.ip_city)
        
        # 如果没有地域信息，返回空
        if not location_parts:
            return ""
        else:
            # 拼接最终结果
            return "-".join(location_parts)
