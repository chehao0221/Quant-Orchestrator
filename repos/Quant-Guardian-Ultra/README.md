# 🛡️ Quant-Guardian-Ultra | 量化守護者
> **基於 XGBoost AI 預測與 Discord 多頻道自動化分流的智能交易監控系統**

---

## 🚀 系統核心功能
本系統部署於 GitHub Actions 雲端環境，結合 **yfinance** 與 **Google News** 數據，實現全天候四個關鍵時段的自動化監控與預測。

### 📡 Discord 四路訊息分流
系統透過 Webhooks 將不同性質的資訊發送到獨立頻道，避免資訊過載：

* **🚨 黑天鵝頻道**：針對市場極端恐慌 (VIX > 35) 與災難性新聞提供紅色警戒。
* **📰 焦點消息頻道**：提供台/美股盤前焦點，具備內容 Hash 去重功能，保證不重複推播。
* **📈 台股分析頻道**：每日 14:30 推送台股重點個股 (2330, 2317...) 的 AI 盤後預測報告。
* **🇺🇸 美股分析頻道**：每日 06:00 推送美股重點個股 (NVDA, TSLA...) 的 AI 盤後收盤報告。

---

## ⏰ 自動化任務時間表 (台灣時間 UTC+8)
| 時間 | 任務內容 | 目標頻道 |
| :--- | :--- | :--- |
| **06:00** | 美股盤後 AI 分析報告 | 🇺🇸 US Stock |
| **08:00** | 台股盤前焦點掃描 + 風險監控 | 📰 News / 🚨 Swan |
| **14:30** | 台股盤後 AI 分析報告 + 午後焦點 | 📈 TW Stock / 📰 News |
| **20:00** | 美股盤前焦點掃描 + 風險監控 | 📰 News / 🚨 Swan |

---

## 🛠️ 技術棧與架構
- **開發語言**: Python 3.10
- **AI 模型**: XGBoost Classifier/Regressor
- **數據來源**: Yahoo Finance API, Google News RSS
- **自動化運算**: GitHub Actions (Ubuntu-latest)
- **通知中樞**: Discord Webhooks SDK

## 📁 資料夾結構說明
- `core/`: 系統核心邏輯 (Notifier, DataManager)
- `modules/`: 掃描器與分析模型模組
- `data/`: 存儲歷史紀錄 (CSV) 與系統狀態 (JSON)
- `entrypoint.py`: 系統排程執行主程式

---
**免責聲明：** 本系統之 AI 預測結果僅供參考，不構成投資建議。金融市場有風險，投資需謹慎。

```
Quant-Guardian-Ultra/
│
├─ .github/workflows/
│  └─ main_pipeline.yml       # 核心自動化排程 (UTC+8 06:00, 08:00, 14:30, 20:00)
│
├─ core/                      # 核心邏輯庫
│  ├─ engine.py               # 風控管理與 L1-L4 分級控制器
│  ├─ model.py                # XGBoost 預測模型封裝
│  ├─ data_manager.py         # CSV/JSON 數據讀寫中樞
│  └─ notifier.py             # Discord 4 頻道分流發送器
│
├─ modules/                   # 功能組件
│  ├─ scanners/               # 市場偵測 (News, VIX, Price)
│  │    ├─ news.py            # 新聞爬蟲與指紋去重
│  │    └─ vix_scanner.py     # VIX 恐慌指數監控
│  ├─ analysts/               # AI 策略模組
│  │    └─ market_analyst.py  # 台/美股市場趨勢分析
│  └─ guardians/              # 守護邏輯
│       └─ defense.py         # 極端風險防禦機制
│
├─ data/                      # 數據持久層
│  ├─ history/                # 台美股分析歷史紀錄
│  ├─ models/                 # AI 模型權重檔
│  └─ system/                 # 系統狀態與去重 Hash (state.json)
│
├─ entrypoint.py              # 系統啟動入口 (智慧時間分流)
├─ requirements.txt           # 環境依賴清單
└─ README.md                  # 項目說明文件
```

DISCORD_TW_STOCK (台股報告)

DISCORD_US_STOCK (美股報告)

DISCORD_BLACK_SWAN (黑天鵝緊急警報)

DISCORD_GENERAL_NEWS (一般市場消息)


