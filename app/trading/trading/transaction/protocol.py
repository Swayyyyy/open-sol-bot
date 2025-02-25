from enum import Enum


class TradingRoute(Enum):
    """交易路由类型，表示不同的交易方式"""

    PUMP = "pump"  # PUMP 协议交易
    RAYDIUM_V4 = "raydium_v4"  # Raydium V4 协议交易
    DEX = "dex"  # DEX 交易

    @classmethod
    def from_str(cls, value: str) -> "TradingRoute":
        """从字符串创建交易路由类型

        Args:
            value (str): 交易路由类型字符串

        Returns:
            TradingRoute: 交易路由类型枚举

        Raises:
            ValueError: 如果字符串不是有效的交易路由类型
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid trading route: {value}. Must be one of: {[e.value for e in cls]}"
            )
