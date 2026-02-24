from __future__ import annotations

from dataclasses import asdict
import time

import streamlit as st

from tradebot.app.bot_service import BotService
from tradebot.config.settings import BotConfig, load_config
from tradebot.loggingx.logger import sanitize_secret

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


def init_state() -> None:
    cfg = load_config()
    defaults = {
        "cfg": cfg,
        "bot": BotService(cfg),
        "running": False,
        "last_decision_ts": 0.0,
        "last_snapshot": None,
        "close_all_confirm": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sidebar_controls() -> BotConfig:
    cfg: BotConfig = st.session_state["cfg"]
    st.sidebar.header("Bot Controls")
    provider = st.sidebar.selectbox("Provider", ["RuleBased", "OpenAI", "Gemini", "Ollama"], index=["RuleBased", "OpenAI", "Gemini", "Ollama"].index(cfg.decider_provider))
    model_map = {
        "RuleBased": ["rule-v1"],
        "OpenAI": ["gpt-4o-mini", "gpt-4.1-mini"],
        "Gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "Ollama": ["llama3.1", "mistral"],
    }
    model = st.sidebar.selectbox("Model", model_map[provider])
    symbol = st.sidebar.text_input("Symbol", value=cfg.default_symbol).upper()
    market_type = st.sidebar.selectbox("Market Type", ["spot", "futures"], index=["spot", "futures"].index(cfg.market_type))
    mode = st.sidebar.selectbox("Mode", ["paper", "demo", "live"], index=["paper", "demo", "live"].index(cfg.bot_mode))
    decision_interval = st.sidebar.number_input("Decision interval (sec)", min_value=1, value=int(cfg.decision_interval_seconds))
    ui_refresh = st.sidebar.number_input("UI refresh interval (sec)", min_value=1, value=int(cfg.ui_refresh_interval_seconds))
    emergency_stop = st.sidebar.toggle("Emergency Stop", value=st.session_state["bot"].emergency_stop)

    updated = BotConfig(**{**asdict(cfg),
        "decider_provider": provider,
        "decider_model": model,
        "default_symbol": symbol,
        "market_type": market_type,
        "bot_mode": mode,
        "decision_interval_seconds": int(decision_interval),
        "ui_refresh_interval_seconds": int(ui_refresh),
    })
    st.session_state["cfg"] = updated
    st.session_state["bot"].set_emergency_stop(emergency_stop)
    return updated


def control_buttons(cfg: BotConfig) -> None:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Start", width="stretch"):
            st.session_state["bot"] = BotService(cfg)
            st.session_state["running"] = True
            st.session_state["last_decision_ts"] = 0.0
    with c2:
        if st.button("Stop", width="stretch"):
            st.session_state["running"] = False
    with c3:
        if st.button("Run Once", width="stretch"):
            st.session_state["last_snapshot"] = st.session_state["bot"].run_once()
            st.session_state["last_decision_ts"] = time.time()
    with c4:
        if st.button("Close All Positions", width="stretch"):
            st.session_state["close_all_confirm"] = True

    if st.session_state.get("close_all_confirm"):
        st.warning("Close All için onay verin")
        if st.checkbox("Evet, tüm pozisyonları kapat", key="confirm_close_all"):
            st.session_state["last_snapshot"] = st.session_state["bot"].close_all_positions()
            st.session_state["close_all_confirm"] = False


def tick_runtime() -> None:
    bot: BotService = st.session_state["bot"]
    cfg: BotConfig = st.session_state["cfg"]
    now = time.time()

    if st.session_state["running"] and now - st.session_state["last_decision_ts"] >= cfg.decision_interval_seconds:
        st.session_state["last_snapshot"] = bot.run_once()
        st.session_state["last_decision_ts"] = now
    else:
        # Decision zamanı gelmese bile UI tarafında balance/position/pnl canlı yenilensin.
        st.session_state["last_snapshot"] = bot.refresh_only()


def render_panels(snapshot: dict) -> None:
    cards = snapshot["account_cards"]
    a, b, c, d, e = st.columns(5)
    a.metric("Wallet Balance", f"{cards['wallet_balance']:.2f}")
    b.metric("Available Balance", f"{cards['available_balance']:.2f}")
    c.metric("Equity", f"{cards['equity']:.2f}")
    d.metric("Unrealized PnL", f"{cards['unrealized_pnl']:.2f}")
    e.metric("Realized PnL(Session)", f"{cards['realized_pnl']:.2f}")

    st.caption("Not: Paper modda bakiye/pozisyon simülasyon verisidir. Demo/Live modda spot için USDT bakiyesi test hesaptan senkronlanır.")
    st.subheader("Open Positions")
    st.dataframe(snapshot["positions"], width="stretch")
    st.subheader("Last Decision")
    st.json(snapshot["last_decision"])
    st.subheader("Recent Orders")
    st.dataframe(snapshot["recent_orders"], width="stretch")
    st.subheader("Order Result")
    st.json(snapshot["order_result"])
    st.subheader("Recent Logs")
    st.code("\n".join(snapshot["logs"][:30]))
    if snapshot.get("error"):
        st.error(snapshot["error"])


def main() -> None:
    st.set_page_config(page_title="TradeBot Live Monitor", layout="wide")
    init_state()
    cfg = sidebar_controls()
    control_buttons(cfg)

    if st_autorefresh:
        st_autorefresh(interval=cfg.ui_refresh_interval_seconds * 1000, key="ui_refresh")
    else:
        st.info("Auto refresh eklentisi yok; canlı güncelleme için streamlit-autorefresh paketini kurun.")

    st.caption(
        f"Python {cfg.python_version} | Mode={cfg.bot_mode} | Market={cfg.market_type} | LiveEnabled={cfg.live_trading_enabled} | API={sanitize_secret(cfg.binance_api_key)}"
    )
    if cfg.bot_mode == "live" and not cfg.live_trading_enabled:
        st.warning("Live mode seçili fakat LIVE_TRADING_ENABLED=false. Emirler engellenecek.")
    if cfg.bot_mode in {"demo", "live"} and cfg.market_type == "futures":
        st.warning("Futures demo/live order entegrasyonu bu MVP'de tamamlanmadı. Spot testnet kullanın.")

    tick_runtime()
    render_panels(st.session_state["last_snapshot"])


if __name__ == "__main__":
    main()
