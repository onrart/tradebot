from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PaperWallet:
    wallet_balance: float
    available_balance: float
    base_qty: float = 0.0
    entry_price: float = 0.0

    def buy(self, price: float, quote_amount: float) -> float:
        spend = min(self.available_balance, quote_amount)
        if price <= 0 or spend <= 0:
            return 0.0
        qty = spend / price
        prev_cost = self.base_qty * self.entry_price
        self.base_qty += qty
        self.available_balance -= spend
        self.entry_price = (prev_cost + spend) / self.base_qty
        return qty

    def sell(self, price: float, qty: float) -> tuple[float, float]:
        qty = min(self.base_qty, qty)
        if qty <= 0:
            return 0.0, 0.0
        realized = (price - self.entry_price) * qty
        proceeds = qty * price
        self.base_qty -= qty
        self.available_balance += proceeds
        self.wallet_balance += realized
        if self.base_qty == 0:
            self.entry_price = 0.0
        return qty, realized
