# Quant-Orchestrator

## 📌 專案定位

**Quant-Orchestrator 是一個「排程與協調層」倉庫。**

本倉庫 **不包含任何交易、分析或風控邏輯**，  
只負責在正確的時間點，啟動正確的子系統。

> 👉 Orchestrator ≠ Strategy  
> 👉 Orchestrator ≠ Risk Engine  
> 👉 Orchestrator = Scheduler Only

---

## 🧠 系統角色說明

本系統負責協調以下兩個（或以上）獨立專案：

### 🔴 Quant-Guardian-Ultra
- 系統安全與風控層
- 新聞去重、防洗版
- 黑天鵝（L4）防禦
- 系統狀態記憶（state.json）
- **保證整體系統「不爆、不失控」**

### 🔵 Stock-Genius-System
- 研究 / AI 分析層
- 台股 / 美股 AI 預測
- Explorer（Lv2）探索池
- 僅輸出分析結果
- **不做任何風控或決策**

---

## 🧩 架構總覽

```
Quant-Orchestrator/
│
├─ .github/
│  └─ workflows/
│     ├─ guardian.yml          # 🚨 只負責跑 Quant-Guardian-Ultra
│     │                        # - 新聞雷達
│     │                        # - 黑天鵝 / L4 風控
│     │
│     ├─ genius.yml            # 📈 只負責跑 Stock-Genius-System（Lv1）
│     │                        # - 台股 / 美股 AI 核心監控
│     │
│     └─ explorer.yml          # 🧭 Explorer / Lv2（可選）
│                              # - 成交量 Top 500 股池更新
│                              # - Explorer AI 潛力股排序
│
├─ repos/
│  ├─ Quant-Guardian-Ultra/    # 🛡 風控系統（原封不動 clone）
│  │   ├─ core/
│  │   ├─ modules/
│  │   ├─ data/
│  │   ├─ entrypoint.py
│  │   └─ requirements.txt
│  │
│  └─ Stock-Genius-System/     # 🧠 AI 分析系統（原封不動 clone）
│      ├─ scripts/
│      ├─ data/
│      ├─ requirements.txt
│      └─ README.md
│
├─ shared/                     # 🔒 預留共享狀態層（目前未啟用）
│  └─ state.json
│
└─ README.md                   # 📘 本文件（系統說明 / 架構圖 / 排程策略）


```

---

## ⚠️ 重要設計原則（請勿違反）

### 1️⃣ Orchestrator 不包含邏輯
- 不 import 子專案程式碼
- 不讀寫子專案 data
- 不共享狀態（目前）

### 2️⃣ 子專案必須「完整存在」
- `repos/Quant-Guardian-Ultra` 為完整 repo
- `repos/Stock-Genius-System` 為完整 repo
- 有更新 → **整包覆蓋**

### 3️⃣ 唯一溝通方式 = 執行入口
- Guardian：`python entrypoint.py`
- Genius：由其內部 workflow / scripts 自行控制

---

## ⏱ 排程說明（概念）

- `guardian.yml`
  - 高優先級
  - 防止重複播報
  - 防止系統失控

- `genius.yml`
  - 研究與分析用途
  - 可調整頻率
  - 不影響風控

- `explorer.yml`
  - 可選
  - 僅探索用
  - 允許中斷、不影響主系統

---

## 🔒 使用聲明

- 本系統僅供 **研究 / 教學 / 技術驗證**
- 所有輸出皆為機率推估
- **不構成任何投資建議**
- 使用者需自行承擔一切風險

---

## 🧘 結語

如果你在這個 repo 想「加邏輯」，  
那代表你應該去改 **子專案**，而不是這裡。


| 類型        | Discord Secret 名稱            | 用途               |
| --------- | ---------------------------- | ---------------- |
| 一般系統 / 新聞 | `DISCORD_WEBHOOK_GENERAL`    | 系統狀態、一般新聞        |
| 黑天鵝       | `DISCORD_WEBHOOK_BLACK_SWAN` | L4 / 極端風險        |
| 美股        | `DISCORD_WEBHOOK_US`         | 美股 AI / Explorer |
| 台股        | `DISCORD_WEBHOOK_TW`         | 台股 AI / Explorer |


> **Quant-Orchestrator 只做一件事：  
> 在對的時間，叫對的人起床。**


