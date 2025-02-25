from dataclasses import asdict, dataclass

import orjson as json


@dataclass
class BotSetting:
    wallet_address: str
    chat_id: int
    pk: int | None = None
    auto_slippage: bool = True
    quick_slippage: int = 1500  # 15%
    min_slippage: int = 250  # 2.5%
    max_slippage: int = 3000  # 30%
    sandwich_mode: bool = False
    sandwich_slippage_bps: int = 5000  # 50%
    buy_priority_fee: float = 0.0001  # SOL
    sell_priority_fee: float = 0.0001  # SOL
    auto_buy: bool = False
    auto_sell: bool = False
    custom_buy_amount_1: float = 0.05  # SOL
    custom_buy_amount_2: float = 0.1
    custom_buy_amount_3: float = 0.5
    custom_buy_amount_4: float = 1
    custom_buy_amount_5: float = 3
    # 自定义卖出的按钮份额
    custom_sell_amount_1: float = 0.5  # %
    custom_sell_amount_2: float = 1  # %

    def set_quick_slippage(self, slippage: float):
        """设置快速滑点

        Args:
            slippage (float): 0-100%
        """
        self.quick_slippage = int(slippage * 100)

    def get_quick_slippage_pct(self) -> float:
        """获取快速滑点（%）

        Returns:
            float: 0-100%
        """
        return self.quick_slippage / 100

    def set_sandwich_slippage(self, slippage: float):
        """设置防夹滑点

        Args:
            slippage (float): 0-100%
        """
        self.sandwich_slippage_bps = int(slippage * 100)

    def get_sandwich_slippage_pct(self) -> float:
        """获取防夹滑点（%」

        Returns:
            float: 0-100%
        """
        return self.sandwich_slippage_bps / 100

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        return cls(**json.loads(json_str))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
