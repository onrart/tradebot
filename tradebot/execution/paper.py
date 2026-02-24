from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PaperWallet:
    quote_balance: float
    base_qty: float = 0.0
    entry_price: float = 0.0

    def equity(self, last_price: float) -> float:
        return self.quote_balance + self.base_qty * last_price

    def buy(self, price: float, quote_amount: float) -> float:
        spend = min(self.quote_balance, quote_amount)
        qty = spend / price if price > 0 else 0.0
        if qty <= 0:
            return 0.0
        prev_cost = self.base_qty * self.entry_price
        self.base_qty += qty
        self.quote_balance -= spend
        self.entry_price = (prev_cost + spend) / self.base_qty
        return qty

    def sell(self, price: float, qty: float) -> float:
        qty = min(self.base_qty, qty)
        if qty <= 0:
            return 0.0
        self.base_qty -= qty
        self.quote_balance += qty * price
        if self.base_qty == 0:
            self.entry_price = 0.0
        return qty
