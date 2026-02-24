# TradeBot MVP (Python 3.11+, Binance + Streamlit + LLM)

Modüler, güvenli ve hata toleranslı bir trade bot MVP'si.

## Temel Özellikler
- Varsayılan mod: `paper`.
- `demo/testnet` destekli, `live` sadece `LIVE_TRADING_ENABLED=true` ise aktif.
- Varsayılan `MARKET_TYPE=spot` (testnet order görünürlüğü için).
- Decision interval default **10s** (`DECISION_INTERVAL_SECONDS`) ve UI override.
- UI refresh interval decision'dan bağımsız (`UI_REFRESH_INTERVAL_SECONDS`, default 2s).
- LLM decider adapterları: RuleBased / OpenAI / Gemini / Ollama.
- Demo/Live modda spot testnet için gerçek emir entegrasyonu vardır (API key/secret gerekir).
- Futures demo/live order akışı TODO olarak işaretlidir.
- Canlı izleme paneli: bakiye kartları, açık pozisyonlar, unrealized/realized PnL, son karar, emir geçmişi, log.

## Mimari
- `tradebot/app`: orchestrator/runtime
- `tradebot/config`: `.env` config yükleme
- `tradebot/data`: market data fetch
- `tradebot/indicators`: EMA/RSI/ATR
- `tradebot/deciders`: karar katmanı + fallback
- `tradebot/exchange`: Binance spot/futures abstraction
- `tradebot/execution`: validation + order simulation
- `tradebot/portfolio`: position & PnL normalize
- `tradebot/risk`: risk guard'lar
- `tradebot/history`: local order state persistence
- `tradebot/loggingx`: JSON structured log + UI log feed

## Çalıştırma
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run streamlit_app.py
```

## Güvenlik
- Secret değerler loglanmaz (maskelenir).
- Live guard açık değilse live emirleri bloklanır.
- Emergency Stop yeni order açmayı durdurur.

## Test
```bash
pytest -q
```

## Bilinen Eksikler / TODO
- Binance signed order endpointleri demo/live için placeholder.
- Websocket yerine şu an REST refresh/polling yaklaşımı.
- Advanced risk (drawdown/leverage guard) genişletilebilir.
- Backtest/performance analytics modülü henüz yok.
