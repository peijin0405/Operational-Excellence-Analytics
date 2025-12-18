# Operational-Excellence-Analytics

## 📊 Metrics Definition

This project evaluates individual productivity using **volume-normalized efficiency metrics** to ensure fair comparison under fluctuating workloads.

---

### 1. Relative Efficiency (Normalized Efficiency)

**Relative Efficiency** measures an employee’s productivity **relative to the average productivity within the same labor company and the same time bin**, removing the effect of system-level volume fluctuations.

#### Formula

For employee *i* at time bin *t*:

\[
\text{Relative Efficiency}_{i,t}
=
\frac{\text{Scans}_{i,t}}
{\frac{1}{N}\sum_{j=1}^{N}\text{Scans}_{j,t}}
\]

Where:
- \(\text{Scans}_{i,t}\): number of scans completed by employee *i* during time bin *t*
- \(N\): number of employees in the **same labor company**
- The denominator represents the **company-level average scans** at time *t*

#### Interpretation
- **1.0** → performance equals the company average for that hour  
- **> 1.0** → above-average efficiency  
- **< 1.0** → below-average efficiency  

This normalization removes hour-level volume effects and enables **fair within-company comparison**.

---

### 2. De-trended CV (De-trended Coefficient of Variation)

**De-trended CV** measures how **stable** an employee’s performance is after removing systematic workload patterns.

#### Step 1: De-trended Residual

\[
\text{Residual}_{i,t}
=
\text{Scans}_{i,t}
-
\frac{1}{N}\sum_{j=1}^{N}\text{Scans}_{j,t}
\]

This residual captures how much employee *i* deviates from the company average at time bin *t*.

#### Step 2: De-trended CV

\[
\text{DeTrended CV}_{i}
=
\frac{\sigma(\text{Residual}_{i,t})}
{\mu(\text{Scans}_{i,t})}
\]

Where:
- \(\sigma(\cdot)\): standard deviation across time bins
- \(\mu(\text{Scans}_{i,t})\): mean raw scan count of employee *i*

#### Interpretation
- **Lower values** → more stable performance across time  
- **Higher values** → greater variability, even after workload trends are removed  

Unlike raw CV, De-trended CV reflects **individual inconsistency rather than system-level volume fluctuation**.

---

### 📌 Why These Metrics Are Used Together

| Metric | Captures | Key Question |
|------|--------|-------------|
| Relative Efficiency | Performance level | *How efficient is the worker compared to peers?* |
| De-trended CV | Stability | *How consistent is the worker under varying workloads?* |

Together, these metrics enable **volume-adjusted, within-company productivity evaluation**.

---

### 🔍 Project Notes

- All normalizations are computed **within each labor company**, not across the entire workforce.
- Time bins are treated as independent workload periods.
- Metrics are designed for **intra-company benchmarking**, not cross-company ranking.



## 📊 指标定义（Metrics Definition）

本项目通过**去除货量波动影响的效率指标**，对个体作业效率进行公平评估，避免因不同时段系统货量差异而造成的偏差。

---

### 1. 相对效率（Relative Efficiency / Normalized Efficiency）

**相对效率**用于衡量某一员工在某个时间段内的作业表现，相对于**同一劳务公司、同一时间段内员工平均水平**的高低。

#### 公式

对于员工 *i* 在时间段 *t*：

\[
\text{相对效率}_{i,t}
=
\frac{\text{扫描量}_{i,t}}
{\frac{1}{N}\sum_{j=1}^{N}\text{扫描量}_{j,t}}
\]

其中：
- \(\text{扫描量}_{i,t}\)：员工 *i* 在时间段 *t* 内完成的扫描数量  
- \(N\)：**同一劳务公司**内参与该时间段作业的员工数量  
- 分母表示该时间段内，公司层面的平均扫描量

#### 指标含义
- **= 1.0**：效率等于公司平均水平  
- **> 1.0**：高于公司平均效率  
- **< 1.0**：低于公司平均效率  

该指标通过对时间段进行归一化处理，有效消除了**系统货量波动**带来的影响，适用于**公司内部员工效率对比**。

---

### 2. 去趋势 CV（De-trended Coefficient of Variation）

**去趋势 CV**用于衡量在排除系统性货量波动后，员工个人效率的**稳定性**。

#### 第一步：去趋势残差（Residual）

\[
\text{残差}_{i,t}
=
\text{扫描量}_{i,t}
-
\frac{1}{N}\sum_{j=1}^{N}\text{扫描量}_{j,t}
\]

该残差表示员工 *i* 在时间段 *t* 相对于公司平均水平的偏离程度。

#### 第二步：去趋势 CV

\[
\text{去趋势 CV}_{i}
=
\frac{\sigma(\text{残差}_{i,t})}
{\mu(\text{扫描量}_{i,t})}
\]

其中：
- \(\sigma(\cdot)\)：员工在多个时间段上的残差标准差  
- \(\mu(\text{扫描量}_{i,t})\)：员工的原始扫描量平均值  

#### 指标含义
- **数值越小**：员工表现越稳定  
- **数值越大**：员工在不同时段的表现波动越大  

与直接使用原始扫描量计算 CV 不同，去趋势 CV 更能反映**员工自身的作业稳定性**，而非系统货量变化。

---

### 📌 指标组合使用说明

| 指标 | 衡量维度 | 回答的问题 |
|----|--------|----------|
| 相对效率 | 作业水平 | 员工的效率是否高于同公司平均水平？ |
| 去趋势 CV | 稳定性 | 员工在不同货量条件下是否稳定？ |

两个指标结合使用，可以同时刻画员工的**效率水**
