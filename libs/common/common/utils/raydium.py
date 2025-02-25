import httpx


class RaydiumAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://api-v3.raydium.io/",
        )

    async def get_pool_info(self, pool_id: str) -> dict:
        params = {
            "ids": pool_id,
        }
        response = await self.client.get("/pools/info/ids", params=params)
        response.raise_for_status()
        return response.json()

    async def get_pool_info_by_mint(
        self,
        mint: str,
        pool_type: str = "all",
        sort_field: str = "default",
        sort_type: str = "desc",
        page_size: int = 10,
        page: int = 1,
    ) -> dict:
        """获取池子信息

        {
          "id": "e971199e-dd0a-479e-a666-3d9c12e07cd8",
          "success": true,
          "data": {
            "count": 1,
            "data": [
              {
                "type": "Standard",
                "programId": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
                "id": "FDsr35mYGXKPepcHSC2cUsqwgotamjJHQEHYvPFvXEox",
                "mintA": {
                  "chainId": 101,
                  "address": "Cy6dgrvCrrBjYYRL19VjA2X25Mt3V7wb4g6YbQ4SEXF2",
                  "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                  "logoURI": "",
                  "symbol": "",
                  "name": "",
                  "decimals": 6,
                  "tags": [],
                  "extensions": {}
                },
                "mintB": {
                  "chainId": 101,
                  "address": "So11111111111111111111111111111111111111112",
                  "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                  "logoURI": "https://img-v1.raydium.io/icon/So11111111111111111111111111111111111111112.png",
                  "symbol": "WSOL",
                  "name": "Wrapped SOL",
                  "decimals": 9,
                  "tags": [],
                  "extensions": {}
                },
                "price": 0.000024273049410341493,
                "mintAmountA": 4629226.752166,
                "mintAmountB": 112.365449687,
                "feeRate": 0.0025,
                "openTime": "1735789105",
                "tvl": 45840.19,
                "day": {
                  "volume": 462360.846222525,
                  "volumeQuote": 2593.561306194845,
                  "volumeFee": 1155.902115556308,
                  "apr": 920.38,
                  "feeApr": 920.38,
                  "priceMin": 1.4200501253132854e-7,
                  "priceMax": 0.0001525308153887998,
                  "rewardApr": []
                },
                "week": {
                  "volume": 462360.846222525,
                  "volumeQuote": 2593.561306194845,
                  "volumeFee": 1155.902115556308,
                  "apr": 75.65,
                  "feeApr": 75.65,
                  "priceMin": 1.4200501253132854e-7,
                  "priceMax": 0.0001525308153887998,
                  "rewardApr": []
                },
                "month": {
                  "volume": 462360.846222525,
                  "volumeQuote": 2593.561306194845,
                  "volumeFee": 1155.902115556308,
                  "apr": 30.26,
                  "feeApr": 30.26,
                  "priceMin": 1.4200501253132854e-7,
                  "priceMax": 0.0001525308153887998,
                  "rewardApr": []
                },
                "pooltype": [
                  "OpenBookMarket"
                ],
                "rewardDefaultInfos": [],
                "farmUpcomingCount": 0,
                "farmOngoingCount": 0,
                "farmFinishedCount": 0,
                "marketId": "MneCkaJoRJNGtT2LSXfhh3ntukq7sodvXn4cr7wwnQL",
                "lpMint": {
                  "chainId": 101,
                  "address": "4piay4w9j34qrteJ1UN12w8f97fx3Ah1D7pCNiRJbV2k",
                  "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                  "logoURI": "",
                  "symbol": "",
                  "name": "",
                  "decimals": 6,
                  "tags": [],
                  "extensions": {}
                },
                "lpPrice": 0.06482781885111535,
                "lpAmount": 707106.781186,
                "burnPercent": 100
              }
            ],
            "hasNextPage": false
          }
        }
        """
        params = {
            "mint1": mint,
            "poolType": pool_type,
            "poolSortField": sort_field,
            "sortType": sort_type,
            "pageSize": page_size,
            "page": page,
        }
        response = await self.client.get("/pools/info/mint", params=params)
        response.raise_for_status()
        data = response.json()
        if data["success"]:
            return data["data"]
        raise ValueError(f"Failed to fetch pool info: {data}")
