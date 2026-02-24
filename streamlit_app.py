from __future__ import annotations

import time
from dataclasses import asdict

import streamlit as st

from tradebot.app.bot_service import BotService
from tradebot.config.settings import BotConfig, load_config
from tradebot.utils.logger import sanitize_secret

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:  # optional dependency fallback
    st_autorefresh = None


def init_state() -> None:
    defaults = {
        "cfg": load_config(),
        "bot": None,
        "running": False,
        "next_tick_ts": 0.0,
        "last_snapshot": None,
        "ui_error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sidebar_controls() -> BotConfig:
    cfg: BotConfig = st.session_state["cfg"]
    st.sidebar.header("TradeBot Settings")
    provider = st.sidebar.selectbox("Decider", ["RuleBased", "OpenAI", "Gemini", "Ollama"], index=["RuleBased", "OpenAI", "Gemini", "Ollama"].index(cfg.provider))
    default_models = {
        "RuleBased": ["rule-v1"],
        "OpenAI": ["gpt-4o-mini", "gpt-4.1-mini"],
        "Gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "Ollama": ["llama3.1", "mistral"],
    }
    model = st.sidebar.selectbox("Model", default_models[provider])
    symbol = st.sidebar.text_input("Coin", value=cfg.symbol).upper()
    mode = st.sidebar.selectbox("Mode", ["paper", "demo", "live"], index=["paper", "demo", "live"].index(cfg.mode))
    interval_options = [10, 30, 40, 50, 60]
    default_interval = cfg.interval_seconds if cfg.interval_seconds in interval_options else 10
    interval = st.sidebar.selectbox(
        "Tick interval (sn)",
        interval_options,
        index=interval_options.index(default_interval),
    )
    custom_interval = st.sidebar.number_input("Custom interval", min_value=5, value=int(interval), step=1)

    updated = BotConfig(**{**asdict(cfg), "provider": provider, "model": model, "symbol": symbol, "mode": mode, "interval_seconds": int(custom_interval)})
    st.session_state["cfg"] = updated
    return updated


def control_buttons(cfg: BotConfig) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Start", use_container_width=True):
            st.session_state["bot"] = BotService(cfg)
            st.session_state["running"] = True
            st.session_state["next_tick_ts"] = 0.0
    with c2:
        if st.button("Stop", use_container_width=True):
            st.session_state["running"] = False
    with c3:
        if st.button("Run Once", use_container_width=True):
            run_tick(force=True)


def run_tick(force: bool = False) -> None:
    bot = st.session_state.get("bot")
    if bot is None:
        bot = BotService(st.session_state["cfg"])
        st.session_state["bot"] = bot

    now = time.time()
    if force or now >= st.session_state.get("next_tick_ts", 0):
        snap = bot.run_once()
        st.session_state["last_snapshot"] = snap
        st.session_state["next_tick_ts"] = now + st.session_state["cfg"].interval_seconds
        st.session_state["ui_error"] = snap.get("error") or ""


def render_status() -> None:
    snap = st.session_state.get("last_snapshot")
    if not snap:
        st.info("Henüz tick çalışmadı.")
        return
    st.write(f"Mode: **{snap['mode']}** | Symbol: **{snap['symbol']}**")
    k1, k2, k3 = st.columns(3)
    k1.metric("Quote Balance", f"{snap['quote_balance']:.2f}")
    k2.metric("Base Qty", f"{snap['base_qty']:.6f}")
    k3.metric("Equity", f"{snap['equity']:.2f}")
    st.subheader("Last Decision")
    st.json(snap["decision"])
    st.subheader("Order Result")
    st.json(snap["order_result"])
    st.subheader("Recent Orders")
    st.dataframe(snap["recent_orders"], use_container_width=True)
    if snap.get("error"):
        st.error(snap["error"])


def main() -> None:
    st.set_page_config(page_title="TradeBot MVP", layout="wide")
    st.title("Binance TradeBot MVP")
    init_state()
    cfg = sidebar_controls()
    control_buttons(cfg)

    st.caption(
        f"API key: {sanitize_secret(cfg.binance_api_key)} | Testnet: {cfg.binance_testnet} | Live enabled: {cfg.live_trading_enabled}"
    )
    if cfg.mode == "live" and not cfg.live_trading_enabled:
        st.warning("Live mode seçili ancak LIVE_TRADING_ENABLED=false. Emirler engellenir.")

    if st.session_state.get("running"):
        if st_autorefresh:
            st_autorefresh(interval=1000, key="bot_autorefresh")
        run_tick(force=False)

    render_status()


if __name__ == "__main__":
    main()
