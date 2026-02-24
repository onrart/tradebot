# TradeBot MVP (Binance + Streamlit + LLM Deciders)

Bu repo, **paper varsayılan** çalışan modüler bir trade bot MVP'sidir.

## Özellikler
- Streamlit UI: provider/model/symbol/mode/interval seçimi, Start/Stop/Run Once.
- Modlar: `paper`, `demo`, `live` (live guard ile).
- Decider arayüzü: RuleBased, OpenAI, Gemini, Ollama.
- Güvenli fallback: LLM hata verirse karar `hold` veya RuleBased'e geri dönebilir.
- Göstergeler: EMA, RSI, ATR.
- Risk: max position, position size limiti, cooldown.
- Execution: paper simülasyon + demo/live placeholder adapter.
- JSON structured logging.

## Proje yapısı
- `tradebot/app`: bot orkestrasyonu
- `tradebot/config`: config/env yükleme
- `tradebot/data`: market data erişimi
- `tradebot/indicators`: teknik indikatörler
- `tradebot/deciders`: karar katmanı
- `tradebot/exchange`: borsa client wrapper
- `tradebot/execution`: emir yürütme
- `tradebot/risk`: risk kontrolleri
- `tradebot/history`: order geçmişi
- `tradebot/utils`: logger vb.
- `streamlit_app.py`: UI giriş noktası

## Kurulum
```bash
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenleyin
streamlit run streamlit_app.py
```

## Canlı işlem uyarısı
**Live trading ciddi finansal risk içerir.** `LIVE_TRADING_ENABLED=true` olmadan live emir çalışmaz.

## Test
```bash
pytest -q
```

## Sonraki adımlar
- Demo/live için signed order endpointlerinin tamamlanması
- Websocket ile düşük gecikmeli veri akışı
- Backtest modülü
- Gelişmiş risk (drawdown, volatility regime, kill-switch)
