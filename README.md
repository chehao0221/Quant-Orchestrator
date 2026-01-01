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


📦 Quant-Orchestrator — 最終整體架構
```
Quant-Orchestrator/
├─ repos/
│  ├─ Quant-Guardian-Ultra/
│  │  ├─ core/
│  │  ├─ modules/
│  │  │  ├─ analysts/
│  │  │  ├─ guardians/
│  │  │  └─ scanners/
│  │  ├─ entrypoint.py
│  │  ├─ requirements.txt
│  │  └─ README.md
│  │
│  └─ Stock-Genius-System/
│     ├─ scripts/
│     │  ├─ ai_tw_post.py
│     │  ├─ ai_us_post.py
│     │  ├─ ai_jp_post.py
│     │  ├─ ai_crypto_post.py
│     │  ├─ news_radar.py
│     │  ├─ news_buffer.py
│     │  └─ ...
│     ├─ requirements.txt
│     └─ README.md
│
├─ vault/
│  ├─ vault_event_store.py
│  ├─ vault_pool_manager.py
│  ├─ vault_ai_judge.py
│  ├─ vault_retention_executor.py
│  ├─ vault_backtest_writer.py
│  └─ ...
│
├─ utils/
│  ├─ vault_root_guard.py
│  ├─ vault_ai_cleaner.py
│  └─ ...
│
├─ shared/
│  ├─ guardian_state.py
│  ├─ system_state.json
│  └─ ...
│
└─ README.md

```
---
💾 E:\Quant-Vault（外接硬碟實體結構｜可直接複製）
```
Quant-Vault/
├─ LOCKED_RAW/ # 原始不可變資料（事實層）
│ ├─ market_raw/ # 市場原始資料
│ ├─ black_swan/ # 黑天鵝事件紀錄
│ └─ backtest/ # 回測原始輸出（不可重寫）
│ ├─ TW/
│ ├─ US/
│ ├─ JP/
│ └─ CRYPTO/
│
├─ LOCKED_DECISION/ # 決策與治理狀態（可回溯）
│ ├─ guardian/
│ │ └─ guardian_state.json # Guardian 等級 / freeze 狀態
│ │
│ ├─ risk_policy/
│ │ └─ ai_weights.json # AI 權重（僅允許治理流程寫入）
│ │
│ └─ horizon/
│ └─ learning_state.json # AI 學習冷卻 / 記錄
│
├─ STOCK_DB/ # 各市場歷史資料庫
│ ├─ TW/
│ │ ├─ universe/
│ │ ├─ shortlist/
│ │ ├─ core_watch/
│ │ ├─ history/
│ │ └─ cache/
│ │
│ ├─ US/
│ ├─ JP/
│ └─ CRYPTO/
│
├─ TEMP_CACHE/ # 暫存 / 防吵 / 稽核
│ ├─ system_audit_state.json # Discord 防重複通知狀態
│ ├─ cache/
│ ├─ snapshot/
│ └─ tmp/
│
└─ LOG/ # 系統日誌（不做決策依據）
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


