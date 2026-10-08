# 术语校验清单

> CR 输出前的最后一道校验。术语错误是致命伤——一个 VIE/JV 混淆就足以让投资人质疑整份报告的专业度。

---

## 一、法律架构术语（零容错）

| 术语 | 含义 | 适用场景 | 常见混淆 |
|------|------|---------|---------|
| **JV** | Joint Venture，合资企业 | 境内注册、中外合资 | ≠ VIE |
| **VIE** | Variable Interest Entity，协议控制 | 境外上市架构（开曼控股→WFOE→VIE协议→境内运营主体） | ≠ JV，≠ 红筹 |
| **红筹架构** | 境外控股公司直接持有境内股权 | 境外上市、无外资限制行业 | ≠ VIE（VIE 用于外资受限行业） |
| **开曼架构** | 注册在开曼群岛的控股公司 | 美元基金投资、境外 IPO | 是架构的一部分，不是独立架构类型 |
| **WFOE** | Wholly Foreign-Owned Enterprise | VIE 架构中的外商独资企业层 | — |

**校验规则**：
- 公司说"注册在国内某区、没有境外主体" → 大概率是 JV 或纯内资，**不是 VIE**
- 公司说"搭了开曼" → 确认是 VIE 还是红筹
- 不确定时写"架构待确认"，**绝不猜**

---

## 二、融资术语（高频易混）

| 术语 | 含义 | 注意 |
|------|------|------|
| **TS** | Term Sheet，投资条款清单 | 非约束性，≠ 已 close |
| **SAFE** | Simple Agreement for Future Equity | 无估值，转换时定价；≠ CB |
| **CB / 可转债** | Convertible Bond | 有到期日、有利率；≠ SAFE |
| **投前 / Pre-money** | 投资前的公司估值 | ≠ 投后 |
| **投后 / Post-money** | 投前 + 本轮融资金额 | 写 CR 时必须标注"投前"还是"投后" |
| **FA** | Financial Advisor | 写 CR 时：FA 操作信息不入正文 |
| **PV** | Pass Vote（内部否决） | FA 内部术语，不入 CR |
| **DPI** | Distributed to Paid-In | LP 视角的回报指标，CR 中极少用 |

**校验规则**：
- 估值必须标注"投前"或"投后"，不能只写"估值 1 亿"
- SAFE 和 CB 不可互换——前者无到期日，后者有
- "已发 TS" ≠ "已 close"，表述要区分

---

## 三、技术术语拼写（高频错误）

| 正确 | 常见错误 | 说明 |
|------|---------|------|
| **Latent** space | Late space, Latant space | 隐空间 |
| **Diffusion** | Diffussion, Difusion | 扩散模型 |
| **Transformer** | Transformor, Transfomer | — |
| **RL-Bench** | RLBench, RL bench | 具身智能评测基准 |
| **sim-to-real** | sim2real, Sim to Real | 统一用连字符小写 |
| **ego-centric** | egocentric, ego centric | 第一人称视角 |
| **VLA** | 不展开 | Vision-Language-Action |
| **CVPR / NeurIPS / AAAI** | 不加中文翻译 | 顶会名统一大写缩写 |
| **fine-tuning** | finetuning, fine tuning | 统一连字符 |
| **pre-training** | pretraining | 统一连字符 |
| **benchmark** | bench mark | 一个词 |

**校验规则**：
- 技术术语首次出现时可加中文括号注释，后续不重复
- 英文术语保持原始大小写（Latent space 的 L 大写仅在句首）
- 缩写不加点（FPS，不是 F.P.S.）

---

## 四、金额与单位（零容错）

| 规则 | 正确 | 错误 |
|------|------|------|
| 币种必标 | "3000 万人民币""300 万美元" | "3000 万"（什么币？） |
| 行内简写可用 | "4kw 人民币""~1 亿美元" | — |
| 投前/投后必标 | "投后 1 亿美元" | "估值 1 亿美元" |
| 区间用连字号 | "1.6-2 亿" | "1.6～2 亿""1.6 到 2 亿" |
| 约数用 ~ | "~4000 万" | "大约 4000 万" |

---

## 五、输出前三步校验流程

```
Step 1：全文搜索以下高危词，逐个确认
    □ VIE / JV / 红筹 / 开曼 → 是否与公司实际架构一致？
    □ 投前 / 投后 → 每个估值数字是否标注了？
    □ SAFE / CB / TS → 用法是否正确？

Step 2：技术术语拼写检查
    □ Latent（不是 Late）
    □ Diffusion（不是 Diffussion）
    □ 所有英文术语拼写正确

Step 3：金额单位检查
    □ 每个金额都有币种
    □ 每个估值都标注投前/投后
    □ 人民币和美元没有混淆
```

---

*校验清单版本：v1.0*
