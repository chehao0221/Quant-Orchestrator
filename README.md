# Quant-Orchestrator

> **系統定位**
>
> Quant-Orchestrator 是一個「排程與協調層（Orchestration Layer）」  
> 專門負責在正確的時間，啟動正確的量化系統。
>
> ❌ 不做分析  
> ❌ 不訓練模型  
> ❌ 不處理市場資料  
> ✅ 只負責排程與系統解耦

---

## 一、整體目錄結構（最終版）



---

## 🧩 架構總覽

```
Quant-Orchestrator/
│
├─ .github/
│  └─ workflows/
│     │
│     ├─ guardian.yml
│     │   # 🛡 Guardian System
│     │   # - 執行 Quant-Guardian-Ultra
│     │   # - 盤後風控 / 黑天鵝 / 新聞去重
│     │   # - 發送：一般消息 / 黑天鵝
│     │
│     ├─ genius.yml
│     │   # 🧠 Stock Genius System
│     │   # - 執行 Stock-Genius-System
│     │   # - 台股 / 美股 AI 預測
│     │   # - 發送：台股 / 美股
│     │
│     └─ explorer.yml
│         # 🧭 Explorer / Lv2
│         # - 更新成交量 Top 500 股池
│         # - 跑 Explorer AI（只顯示 Top 5）
│         # - 不影響任何風控或歷史
│
├─ repos/
│  │
│  ├─ Quant-Guardian-Ultra/
│  │   # ⚠️ 原封不動 clone（只允許 entrypoint import 修正）
│  │
│  │   ├─ entrypoint.py
│  │   │   # 系統入口
│  │   │   # - 動態加入 core/ modules/ 到 sys.path
│  │   │   # - 呼叫所有 Guardian 元件
│  │   │
│  │   ├─ core/
│  │   │   ├─ engine.py
│  │   │   │   # GuardianEngine
│  │   │   │   # - 風險等級 L1–L4
│  │   │   │   # - pause / resume
│  │   │   │
│  │   │   ├─ notifier.py
│  │   │   │   # Discord 通知器
│  │   │   │   # - news / swan / tw / us
│  │   │   │
│  │   │   ├─ data_manager.py
│  │   │   │   # state.json 讀寫
│  │   │   │
│  │   │   └─ __init__.py
│  │   │
│  │   ├─ modules/
│  │   │   ├─ scanners/
│  │   │   │   ├─ news.py
│  │   │   │   │   # 新聞掃描 + 去重（state.json）
│  │   │   │   │
│  │   │   │   ├─ vix_scanner.py
│  │   │   │   │   # VIX 恐慌指數
│  │   │   │   │
│  │   │   │   └─ __init__.py
│  │   │   │
│  │   │   ├─ guardians/
│  │   │   │   ├─ defense.py
│  │   │   │   │   # 極端風險防禦
│  │   │   │   │
│  │   │   │   └─ __init__.py
│  │   │   │
│  │   │   ├─ analysts/
│  │   │   │   ├─ market_analyst.py
│  │   │   │   │   # 台 / 美股分析
│  │   │   │   │
│  │   │   │   └─ __init__.py
│  │   │   │
│  │   │   └─ __init__.py
│  │   │
│  │   ├─ data/
│  │   │   └─ state.json
│  │   │       # 風險狀態 + 新聞 hash
│  │   │
│  │   ├─ requirements.txt
│  │   └─ README.md
│  │
│  └─ Stock-Genius-System/
│      # ⚠️ 原封不動 clone（AI 預測系統）
│
│      ├─ scripts/
│      │   ├─ ai_tw_post.py
│      │   │   # 🇹🇼 台股 AI
│      │   │
│      │   ├─ ai_us_post.py
│      │   │   # 🇺🇸 美股 AI
│      │   │
│      │   ├─ ai_tw_explorer_post.py
│      │   │   # 🇹🇼 Explorer Lv2
│      │   │
│      │   ├─ ai_us_explorer_post.py
│      │   │   # 🇺🇸 Explorer Lv2
│      │   │
│      │   ├─ update_tw_explorer_pool.py
│      │   │   # 更新台股成交量 Top 500
│      │   │
│      │   ├─ update_us_explorer_pool.py
│      │   │   # 更新美股成交量 Top 500
│      │   │
│      │   └─ safe_yfinance.py
│      │       # Yahoo Finance 安全封裝
│      │
│      ├─ data/
│      │   ├─ tw_history.csv
│      │   ├─ us_history.csv
│      │   ├─ explorer_pool_tw.json
│      │   └─ explorer_pool_us.json
│      │
│      ├─ requirements.txt
│      └─ README.md
│
├─ shared/
│  └─ state.json
│      # （保留位，尚未啟用）
│
└─ README.md
    # Quant-Orchestrator 說明文件
    # - 架構定位
    # - 三個 workflow 職責
    # - Discord 頻道對照

```

---

## 二、Workflow 分工（單一職責原則）

### 1️⃣ guardian.yml — 風控唯一入口

**負責系統**
- Quant-Guardian-Ultra

**職責**
- 新聞雷達掃描
- 黑天鵝事件偵測
- L1 → L4 風險分級
- 去重播報（state.json）

**Discord 頻道**
- 一般 / 系統訊息
- 黑天鵝專用頻道

**原則**
- 不跑 AI
- 不管股池
- 不影響任何其他系統

---

### 2️⃣ genius.yml — Lv1 核心 AI 系統

**負責系統**
- Stock-Genius-System

**職責**
- 🇹🇼 台股核心股 AI
- 🇺🇸 美股核心股 AI
- 固定 Horizon（Freeze）
- 僅輸出預測與歷史觀測

**Discord 頻道**
- 🇹🇼 台股頻道
- 🇺🇸 美股頻道

**原則**
- 不跑 Explorer
- 不做風控
- 不依賴 Guardian 狀態

---

### 3️⃣ explorer.yml — Lv2 Explorer（可選）

**負責系統**
- Stock-Genius-System（Explorer 模組）

**職責**
- 更新台 / 美股成交量 Top 500 股池
- Explorer AI 潛力股排序
- 僅顯示 Top 5

**Discord 頻道**
- 🇹🇼 台股頻道（Explorer 區塊）
- 🇺🇸 美股頻道（Explorer 區塊）

**原則**
- 不寫歷史
- 不影響風控
- 可隨時停用

---

## 三、Discord Webhook 對應表（鎖定）

| 用途 | Secret 名稱 | 使用系統 |
|----|----|----|
| 一般 / 系統 | DISCORD_WEBHOOK_GENERAL | Guardian |
| 黑天鵝 | DISCORD_WEBHOOK_BLACK_SWAN | Guardian |
| 美股 | DISCORD_WEBHOOK_US | Genius / Explorer |
| 台股 | DISCORD_WEBHOOK_TW | Genius / Explorer |

> Quant-Orchestrator 只負責「轉交 Secrets」，不產生任何訊息內容。

---

## 四、為什麼要用 Orchestrator

- GitHub Actions 上限風險 → **排程分流**
- 任務互相卡死 → **系統完全解耦**
- 想停 Explorer → 關 explorer.yml
- 想只留風控 → 只留 guardian.yml
- 未來加新系統 → 新增 workflow 即可

---

## 五、系統不變承諾

- Quant-Guardian-Ultra：❌ 不修改
- Stock-Genius-System：❌ 不修改
- 所有控制只在 `.github/workflows`
- Discord 只靠 Secrets 切換
- 可長期穩定運行

---

## 一句話總結

**Quant-Orchestrator 是指揮官，不是士兵。**  
它只負責：在對的時間，叫對的系統出來工作。

