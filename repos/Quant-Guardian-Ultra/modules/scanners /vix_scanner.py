import yfinance as yf

class VixScanner:
    def check_vix(self):
        try:
            # 獲取 VIX 指數數據
            vix_data = yf.download("^VIX", period="1d", interval="1m", progress=False)
            if vix_data.empty:
                return 1
            
            # 確保取到的是單一數值 (最後一筆成交價)
            # 使用 .iloc[-1] 取得最後一行，['Close'] 取得收盤價，並用 .item() 轉為純數字
            current_vix = vix_data['Close'].iloc[-1]
            
            # 如果還是 Series 或 Array，強制轉換
            if hasattr(current_vix, 'item'):
                current_vix = current_vix.item()

            print(f"📊 當前 VIX 指數: {current_vix:.2f}")

            if current_vix > 35: return 4  # 極端恐慌
            if current_vix > 25: return 3  # 高度警戒
            if current_vix > 20: return 2  # 市場波動
            return 1
        except Exception as e:
            print(f"⚠️ VIX 掃描失敗: {e}")
            return 1
