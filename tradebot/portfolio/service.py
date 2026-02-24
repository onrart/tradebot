from __future__ import annotations

from dataclasses import asdict

from tradebot.models.context import NormalizedPosition


class PortfolioService:
    def __init__(self) -> None:
        self.session_realized_pnl: float = 0.0

    def build_position(self, symbol: str, qty: float, entry_price: float, mark_price: float, opened_at: str | None = None) -> NormalizedPosition:
        side = "long" if qty > 0 else "flat"
        notional = qty * mark_price
        unrealized = (mark_price - entry_price) * qty if qty > 0 else 0.0
        pnl_pct = ((mark_price - entry_price) / entry_price * 100) if qty > 0 and entry_price > 0 else 0.0
        return NormalizedPosition(
            symbol=symbol,
            side=side,
            qty=qty,
            entry_price=entry_price,
            mark_price=mark_price,
            unrealized_pnl=unrealized,
            pnl_pct=pnl_pct,
            position_notional=notional,
            opened_at=opened_at,
        )

    def account_cards(self, wallet_balance: float, available_balance: float, positions: list[NormalizedPosition]) -> dict[str, float]:
        total_unrealized = sum(p.unrealized_pnl for p in positions)
        equity = wallet_balance + total_unrealized
        return {
            "wallet_balance": wallet_balance,
            "available_balance": available_balance,
            "equity": equity,
            "unrealized_pnl": total_unrealized,
            "realized_pnl": self.session_realized_pnl,
        }

    def position_table(self, positions: list[NormalizedPosition]) -> list[dict]:
        return [asdict(p) for p in positions]
