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
│ └─ workflows/
│ ├─ guardian.yml # 🚨 只負責跑 Quant-Guardian-Ultra
│ │ # - 新聞雷達
│ │ # - 黑天鵝 / L4 風控
│ │
│ ├─ genius.yml # 📈 只負責跑 Stock-Genius-System（Lv1）
│ │ # - 台股 / 美股 AI 核心監控
│ │
│ └─ explorer.yml # 🧭 Explorer / Lv2（可選）
│ # - 成交量 Top 500 股池更新
│ # - Explorer AI 潛力股排序
│
├─ repos/
│ ├─ Quant-Guardian-Ultra/ # 🛡 風控系統（原封不動 clone，不可修改）
│ │ ├─ core/
│ │ ├─ modules/
│ │ ├─ data/
│ │ ├─ entrypoint.py
│ │ └─ requirements.txt
│ │
│ └─ Stock-Genius-System/ # 🧠 AI 分析系統（原封不動 clone，不可修改）
│ ├─ scripts/
│ ├─ data/
│ ├─ requirements.txt
│ └─ README.md
│
├─ shared/ # 🔒 預留共享狀態層（目前未啟用）
│ └─ state.json
│
└─ README.md # 📘 本文件（系統說明 / 架構 / 排程策略）
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

