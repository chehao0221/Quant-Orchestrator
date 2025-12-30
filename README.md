# Quant-Orchestrator
AI 市場預測・回測・風控整合系統（非交易）

---

## 一、系統定位（非常重要）

Quant-Orchestrator 是一套 **非交易型 AI 市場觀測系統**，  
專注於：

- 📊 AI 股票預測（研究用途）
- 📈 歷史回測與模型穩定性觀測
- 🛡️ 市場風險判定（紅 / 黃 / 綠）
- 🔔 Discord 定時公告

❌ 不下單  
❌ 不自動交易  
❌ 不連券商  
❌ 不即時喊單  

本系統所有輸出 **僅供研究與市場觀測參考**。

---

## 二、整體架構總覽



```
Quant-Orchestrator/
│
├─ .github/
│  └─ workflows/                     ← GitHub Actions 排程層
│     ├─ guardian.yml                ← Guardian 風控（90 分鐘）
│     ├─ genius_tw.yml               ← 台股 AI（盤後一次）
│     ├─ genius_us.yml               ← 美股 AI（收盤後一次）
│     └─ explorer.yml                ← Explorer 池更新
│
├─ repos/
│  ├─ Quant-Guardian-Ultra/           ← Guardian 風控核心
│  │   │
│  │   ├─ core/
│  │   │   ├─ __init__.py
│  │   │   ├─ engine.py               ← GuardianEngine（evaluate_risk）
│  │   │   ├─ notifier.py             ← Discord 通知（GREEN / YELLOW / RED）
│  │   │   └─ risk_policy.py          ← L0–L5 風控邏輯
│  │   │
│  │   ├─ modules/                    ← Guardian 掃描模組（news / vix 等）
│  │   │   └─ …（你原本的）
│  │   │
│  │   ├─ data/                       ← Guardian 自用資料
│  │   │   └─ …
│  │   │
│  │   ├─ entrypoint.py               ← guardian.yml 入口
│  │   └─ requirements.txt
│  │
│  └─ Stock-Genius-System/            ← 市場分析系統（不交易）
│      │
│      ├─ data/
│      │   ├─ tw_history.csv
│      │   ├─ us_history.csv
│      │   ├─ explorer_pool_tw.json
│      │   ├─ explorer_pool_us.json
│      │   ├─ horizon_policy.json
│      │   ├─ black_swan_history.csv
│      │   ├─ news_cache.json
│      │   ├─ l3_warning.flag
│      │   ├─ l4_active.flag
│      │   ├─ l4_last_end.flag
│      │   ├─ equity_TW.png
│      │   └─ equity_US.png
│      │
│      ├─ scripts/                    ← 所有實際執行腳本
│      │   ├─ guard_check.py           ← ✅ Guardian freeze 檢查（你現在用的）
│      │   │
│      │   ├─ ai_tw_post.py            ← 台股 AI 預測（盤後）
│      │   ├─ ai_us_post.py            ← 美股 AI 預測（收盤後）
│      │   │
│      │   ├─ update_tw_explorer_pool.py
│      │   ├─ update_us_explorer_pool.py
│      │   │
│      │   ├─ news_radar.py
│      │   ├─ performance_dashboard.py
│      │   ├─ safe_yfinance.py
│      │   │
│      │   └─ l4_*.py                  ← L4 / 黑天鵝處理
│      │
│      ├─ requirements.txt
│      ├─ README.md
│      └─ LICENSE
│
├─ shared/
│  └─ guardian_state.json             ← 🔑 全系統唯一風控狀態
│
└─ README.md


```



---

## 三、三大系統角色（責任邊界）

### 🛡️ Guardian（Quant-Guardian-Ultra）

**唯一職責：**
判定「現在是否適合解讀 AI 預測」

- 輸出三種狀態：
  - 🟢 綠（L1–L2）：穩定
  - 🟡 黃（L3）：警戒
  - 🔴 紅（L4）：全面防禦
- 🔴 L4 時：
  - Stock-Genius 停止對外發布
  - Explorer 停止更新
- 每 90 分鐘重新進行 AI 判定
- 不分析個股
- 不產生預測內容

---

### 📈 Stock-Genius-System

**唯一職責：**
在 Guardian 允許時，定時輸出 AI 預測與回測結果

- 🇺🇸 美股 / 🇹🇼 台股分離
- 固定顯示「指定核心標的」
- 自動海選：
  - 交易量前 500
  - 技術面 + 消息面
  - 潛力黑馬 Top 5
- 僅研究用途
- 不交易、不即時、不洗頻

---

### 🧩 Explorer

**唯一職責：**
背景資料與股池更新

- 不對外發聲
- Guardian L4 時暫停
- 提供 AI 模型背景資料

---
```
## 四、Discord Webhook（唯一出口）

| 類型 | Discord Webhook 環境變數 |
|------|--------------------------|
| 一般 / 系統 | DISCORD_WEBHOOK_GENERAL |
| 黑天鵝 | DISCORD_WEBHOOK_BLACK_SWAN |
| 台股 | DISCORD_WEBHOOK_TW |
| 美股 | DISCORD_WEBHOOK_US |
| 日股 | DISCORD_WEBHOOK_JP |
| 虛擬貨幣 | DISCORD_WEBHOOK_CRYPTO |
```

**發送規則：**
- 🔴 → 🟢 僅發一次
- 🟡 → 🟢 需要發
- 綠色穩定狀態不重複通知

---

## 五、時間策略（固定、不重複）

- Guardian：每 90 分鐘
- 美股 AI：收盤後一次
- 台股 AI：收盤後一次
- Explorer：夜間或指定時段

---

## 六、合規聲明

- 本系統不構成任何投資建議
- 所有預測皆為機率推估
- 僅供研究與市場觀測使用

---

## 七、接手原則（三句話）

1. Guardian 決定能不能說話  
2. Stock-Genius 只負責說內容  
3. Explorer 永遠不對外  

違反任一條，系統即不再屬於本設計。

---

## 最終定錨

Quant-Orchestrator 是一套  
**可長期自動運行、風控清楚、對外安全的 AI 市場研究系統。**


