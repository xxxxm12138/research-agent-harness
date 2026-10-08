---
name: deal-modeling
description: |
  交易建模：Cap Table、估值模型（DCF / Comps）、清算优先权、反稀释、ESOP 稀释、Warrant 行权、IRR / MOIC。核心：先读法律文件后动手算；能推导的数字一律写公式。触发词：/captable、/交易建模、"算cap table"、"做股权结构"、"估值模型"、"退出回报"、"稀释计算"。
---

# 交易建模

> 适用范围：Cap Table、估值模型（DCF / Comps）、Liquidation Preference、Anti-dilution、ESOP 稀释、Warrant 行权、IRR / MOIC
> 本仓库只含方法与虚构示例。真实协议、Term Sheet 与 cap table 属于保密材料，不入库。

---

## 铁律（违反任何一条 = 任务失败）

### 铁律 1：先读法律文件，后动手算

- 所有数字必须标注来源（协议第 X 条 / Term Sheet 第 X 项）。
- 草稿 / 试算表只做**格式参考**，数字以法律文件为准。
- 股东名称必须从协议**逐字抄录**，不得意译或简称。

### 铁律 2：Excel 必须区分 Input 与 Formula

- **任何生成的 Excel / 数据表都遵守此规则，不限于 cap table。**
- Input 单元格：硬编码，蓝色字体标识（或数量极少）。
- Formula 单元格：公式引用，改一个输入全表联动。
- 绝不允许把本应是公式的值手工 key-in。

### 铁律 3：格式对齐团队模板

- 以团队内部的 cap table 模板（house template）为准：Times New Roman 11pt、灰色表头、medium 边框。
- 详见 `skills/deal-modeling/references/format-template.md`。

---

## Input vs Formula 分类规则（通用）

### INPUT（允许 key-in 的，且仅有这些）

| 类型 | 说明 | 来源 |
|---|---|---|
| 初始注册资本（各股东份额） | 公司成立时的原始股权 | 章程 / 工商登记 |
| 各投资人投资金额 | 每笔认缴出资 / 投资额 | 增资协议 / SPA |
| 投前估值 | 本轮 pre-money | Term Sheet |
| 汇率 | 协议约定或当日央行中间价 | 协议 / 公开数据 |
| 特殊约定的固定数值 | 如 warrant cap 金额 | 协议条款 |

### FORMULA（必须用公式的，其余一切）

| 计算项 | 公式逻辑 | Excel 示例 |
|---|---|---|
| 本轮总投资额 | = SUM(各投资人) | `=SUM(G7:G11)` |
| 投后估值 | = 投前 + 本轮总额 | `=G15+G6` |
| 每股价格 | = 投前估值 / 投前总股数 | `=G15/D33` |
| 新增注册资本（股数） | = ROUND(投资额 / 每股价格, 0) | `=ROUND(F27/G$17,0)` |
| 各轮后持股比例 | = 该股东股数 / 总股数 | `=H21/$H$33` |
| 各轮后股东总股数 | = 上轮股数 + 本轮新增 | `=D21+G21` |
| Section 小计行 | = SUM(section 内各行) | `=SUM(D21:D23)` |
| 全部合计行 | = 原有股东合计 + 新增投资人合计 | `=D24+D32` |
| 投资额引用 | = 引用上方投资人金额 | `=G7`（避免重复 key-in） |
| RMB 换算列 | = USD 金额 × 汇率单元格 | `=G7*$S$6` |

### 判断原则

> **问自己：这个数字能从其他单元格推导出来吗？**
> - 能 → 必须写公式
> - 不能（原始输入 / 外部给定）→ 允许 key-in

### 公式引用规则

- 用 `$` 锁定行 / 列：比例分母用 `$H$33`（绝对引用）。
- 每股价格用 `G$17`（锁行不锁列，方便横向复制）。
- 汇率用 `$S$6`（全表唯一，绝对引用）。
- 跨 section 引用时标注来源注释。

---

## 强制 4 步流程

### Step 1：条款拆解

**输入**：法律文件（增资协议 / SPA / Term Sheet）　**输出**：约束清单

- [ ] 标的公司全称、注册资本、币种
- [ ] 全部股东全称（逐字抄录）
- [ ] 初始持股比例和对应注册资本金额
- [ ] 本轮投资人、投资金额、目标持股比例
- [ ] 投前 / 投后估值
- [ ] 特殊条款（Pro Rata / Anti-dilution / Warrant / ESOP 预留）
- [ ] 交割条件、时间节点
- [ ] 汇率条款（约定汇率 vs 市场汇率）

### Step 2：法律映射

**输入**：约束清单　**输出**：变量定义表 + 计算体系确认

- [ ] 计算币种（USD / RMB / 双列）
- [ ] 汇率来源和数值
- [ ] 注册资本单位（元 / 万元）
- [ ] 股权计算体系（注册资本制 vs authorized shares）
- [ ] 每股价格计算方式（投前估值 / 投前总股数）
- [ ] Input 清单（哪些数字 key-in）
- [ ] Formula 清单（哪些数字靠算）

### Step 3：数学建模

**输入**：变量定义表　**输出**：完整 Excel（带公式）

1. 先搭表格骨架（行列结构对齐模板）
2. 填入 Input 单元格（仅 key-in）
3. 写入所有 Formula 单元格（公式引用）
4. 加总行必须用 SUM 公式
5. 比例列必须用除法公式（不允许手写百分比）
6. Pro Rata / Anti-dilution 如有，单独 section 处理

### Step 4：常识验证

**输入**：完整 Excel　**输出**：验证报告

- [ ] 各轮持股比例加总 = 100%（公式验证：总计行 = 1）
- [ ] 投资额 / 每股价格 = 新增股数（交叉验证）
- [ ] 投前 + 本轮 = 投后（交叉验证）
- [ ] 稀释比例是否合理（常见：种子轮 15-25%、A 轮 15-20%）
- [ ] 公式联动测试：改一个投资额，下游数字是否正确变化
- [ ] 运行 `skills/deal-modeling/checklist/postflight.md`

一个完整的虚构算例见 `skills/deal-modeling/references/worked-example.md`（测试会校验其中的算术）。

---

## 适用场景扩展

本 Skill 的 Input / Formula 规则和 4 步流程同样适用于：

| 场景 | Input | Formula |
|---|---|---|
| DCF 估值 | 收入假设、折现率、终值倍数 | FCF、NPV、企业价值 |
| Comps 估值 | 可比公司指标、目标公司指标 | 中位数、均值、隐含估值 |
| Liquidation Preference | 优先级、倍数、参与权 | 各轮分配金额 |
| IRR / MOIC | 投资金额、退出金额、时间 | IRR、MOIC、DPI |
| ESOP 稀释 | 池子大小、行权价 | 稀释后比例 |

**核心不变**：只有"给定的"才 key-in，能算的一律公式。

---

## 文件引用

| 文件 | 内容 |
|---|---|
| `skills/deal-modeling/references/术语对照表.md` | 注册资本 / 认缴 / 实缴 / 资本公积的精确定义 |
| `skills/deal-modeling/references/常见交易结构.md` | Pro Rata / Anti-dilution / Warrant 等标准公式 |
| `skills/deal-modeling/references/中国有限公司-股权计算规则.md` | 有限公司 vs 股份公司的差异 |
| `skills/deal-modeling/references/format-template.md` | Excel 格式与公式结构模板 |
| `skills/deal-modeling/references/input-vs-formula-规则.md` | 通用数据表公式规则（详细版） |
| `skills/deal-modeling/references/worked-example.md` | 虚构算例：一轮美元增资的完整 cap table |
| `skills/deal-modeling/checklist/preflight.md` | 动手前必须确认 |
| `skills/deal-modeling/checklist/postflight.md` | 出数后必须验证 |
