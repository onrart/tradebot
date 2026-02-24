from __future__ import annotations

import requests


class BinanceSpotClient:
    def __init__(self, testnet: bool = True) -> None:
        self.base_url = "https://testnet.binance.vision" if testnet else "https://api.binance.com"

    def get_symbol_rules(self, symbol: str) -> dict:
        resp = requests.get(f"{self.base_url}/api/v3/exchangeInfo", params={"symbol": symbol}, timeout=15)
        resp.raise_for_status()
        info = resp.json()["symbols"][0]
        filters = {f["filterType"]: f for f in info["filters"]}
        lot = filters.get("LOT_SIZE", {})
        min_notional = filters.get("MIN_NOTIONAL", {})
        return {
            "step_size": float(lot.get("stepSize", 0.000001)),
            "min_qty": float(lot.get("minQty", 0.0)),
            "min_notional": float(min_notional.get("minNotional", 5.0)),
        }

    def get_latest_price(self, symbol: str) -> float:
        resp = requests.get(f"{self.base_url}/api/v3/ticker/price", params={"symbol": symbol}, timeout=15)
        resp.raise_for_status()
        return float(resp.json()["price"])
