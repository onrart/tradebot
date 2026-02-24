from __future__ import annotations

import requests


class BinanceClient:
    def __init__(self, market_type: str = "spot", testnet: bool = True) -> None:
        self.market_type = market_type
        if market_type == "futures":
            self.base_url = "https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com"
        else:
            self.base_url = "https://testnet.binance.vision" if testnet else "https://api.binance.com"

    def _path(self, endpoint: str) -> str:
        if self.market_type == "futures":
            return f"{self.base_url}/fapi/v1/{endpoint}"
        return f"{self.base_url}/api/v3/{endpoint}"

    def get_symbol_rules(self, symbol: str) -> dict:
        resp = requests.get(self._path("exchangeInfo"), params={"symbol": symbol}, timeout=15)
        resp.raise_for_status()
        symbols = resp.json().get("symbols", [])
        if not symbols:
            return {"step_size": 0.001, "min_qty": 0.0, "min_notional": 5.0, "tick_size": 0.0001}
        info = symbols[0]
        filters = {f["filterType"]: f for f in info.get("filters", [])}
        lot = filters.get("LOT_SIZE", {})
        min_notional = filters.get("MIN_NOTIONAL", filters.get("NOTIONAL", {}))
        price_filter = filters.get("PRICE_FILTER", {})
        return {
            "step_size": float(lot.get("stepSize", 0.001)),
            "min_qty": float(lot.get("minQty", 0.0)),
            "min_notional": float(min_notional.get("minNotional", 5.0)),
            "tick_size": float(price_filter.get("tickSize", 0.0001)),
        }

    def get_latest_price(self, symbol: str) -> float:
        endpoint = "ticker/price"
        resp = requests.get(self._path(endpoint), params={"symbol": symbol}, timeout=15)
        resp.raise_for_status()
        return float(resp.json()["price"])
