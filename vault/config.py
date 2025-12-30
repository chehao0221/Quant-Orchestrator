# config.py
MARKET_CONFIG = {
    "TW": {
        "api_endpoint": "https://api.tw.com",  # 台股數據API端點
        "symbols": ["2330.TW", "2317.TW", "2454.TW", "2412.TW", "2308.TW"],  # 台股市場的股票代碼
        "timezone": "Asia/Taipei",  # 時區設置
        "webhook_url": "YOUR_DISCORD_WEBHOOK_TW",  # 台股 Discord Webhook URL
    },
    "US": {
        "api_endpoint": "https://api.us.com",  # 美股數據API端點
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],  # 美股市場的股票代碼
        "timezone": "America/New_York",  # 時區設置
        "webhook_url": "YOUR_DISCORD_WEBHOOK_US",  # 美股 Discord Webhook URL
    },
    "JP": {
        "api_endpoint": "https://api.jp.com",  # 日股數據API端點
        "symbols": ["7203.T", "6758.T", "9984.T", "8306.T"],  # 日股市場的股票代碼
        "timezone": "Asia/Tokyo",  # 時區設置
        "webhook_url": "YOUR_DISCORD_WEBHOOK_JP",  # 日股 Discord Webhook URL
    },
    "CRYPTO": {
        "api_endpoint": "https://api.crypto.com",  # 加密貨幣數據API端點
        "symbols": ["BTC-USD", "ETH-USD", "SOL-USD"],  # 加密貨幣代碼
        "timezone": "UTC",  # 時區設置
        "webhook_url": "YOUR_DISCORD_WEBHOOK_CRYPTO",  # 加密貨幣 Discord Webhook URL
    }
}
