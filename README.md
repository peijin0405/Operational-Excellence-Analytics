
## Operational Excellence Analytics (Streamlit App)

**Operational Excellence Analytics** is a Streamlit-based analytics application designed for **fine-grained labor productivity management** in operational environments such as logistics, sorting centers, and warehouse operations.

The app transforms raw scan-level data into **actionable operational insights**, enabling managers to understand when, where, and who drives efficiency — and where targeted interventions are needed.

Live Demo

👉 Streamlit App:
https://operational-excellence-analytics-obqccuuuf2as9aprzitfzz.streamlit.app/

<img width="2214" height="1262" alt="ba53a0c88fef1651575e25976598fe3e" src="https://github.com/user-attachments/assets/95abce3d-1b00-48e3-8449-7436da127b91" />

<img width="2221" height="1429" alt="fa00cdd41866ec9548aa1dec05fce11a" src="https://github.com/user-attachments/assets/5bc33b3b-4a87-431e-af31-f5e30d06721d" />

<img width="2167" height="1384" alt="a2cadfab7095f9f458b82ad1ad32d190" src="https://github.com/user-attachments/assets/c13de6d8-0f48-4520-8b65-5ee34d907eff" />

### 📊 Metrics Definition

This project evaluates individual productivity using **volume-normalized efficiency metrics** to ensure fair comparison under fluctuating workloads.

---

#### 1. Relative Efficiency (Normalized Efficiency)

**Relative Efficiency** measures an employee’s productivity **relative to the average productivity within the same labor company and the same time bin**, removing the effect of system-level volume fluctuations.


<img width="1505" height="621" alt="2f1f00d34ad9269df698c2c73060b5c4" src="https://github.com/user-attachments/assets/587c46ec-4400-42fc-bf7f-72dd244c7704" />


##### Interpretation
- **1.0** → performance equals the company average for that hour  
- **> 1.0** → above-average efficiency  
- **< 1.0** → below-average efficiency  

This normalization removes hour-level volume effects and enables **fair within-company comparison**.

---

#### 2. De-trended CV (De-trended Coefficient of Variation)

**De-trended CV** measures how **stable** an employee’s performance is after removing systematic workload patterns.

<img width="1706" height="1026" alt="5d5d252c313b32c0405afd7a2f0cd3c4" src="https://github.com/user-attachments/assets/567610d4-5657-4e14-a44e-c7d2575c982c" />
  

Unlike raw CV, De-trended CV reflects **individual inconsistency rather than system-level volume fluctuation**.

---

#### 📌 Why These Metrics Are Used Together

| Metric | Captures | Key Question |
|------|--------|-------------|
| Relative Efficiency | Performance level | *How efficient is the worker compared to peers?* |
| De-trended CV | Stability | *How consistent is the worker under varying workloads?* |

Together, these metrics enable **volume-adjusted, within-company productivity evaluation**.

---



#### 🔍 Project Notes

- All normalizations are computed **within each labor company**, not across the entire workforce.
- Time bins are treated as independent workload periods.
- Metrics are designed for **intra-company benchmarking**, not cross-company ranking.


### 指标说明（Metrics Definition）

本项目通过 **相对效率（Relative Efficiency / Normalized Efficiency）** 和  
**去趋势 CV（De-trended Coefficient of Variation）** 两个指标，对员工在不同时间段、不同货量条件下的工作表现进行**公平、可解释的评估**。

---

#### 一、相对效率（Relative Efficiency / Normalized Efficiency）

相对效率用于衡量某位员工在某一时间段内的工作效率，**相对于同一劳务公司、同一时间段内其他员工的平均水平**，从而抵消整体货量波动带来的影响。

##### 计算公式

<img width="1582" height="457" alt="0b86da3900c2ee7a1447cfb1eb3ac9e8" src="https://github.com/user-attachments/assets/dedf2cd2-b1f1-414a-91e6-295f7b7bbe76" />


##### 指标解释
- 相对效率 = 1：该员工在该时段的效率等于公司平均水平  
- 相对效率 > 1：高于公司平均效率  
- 相对效率 < 1：低于公司平均效率  

通过这种标准化方式，可以在不同时段货量差异较大的情况下，对员工效率进行公平比较。

---

#### 二、去趋势 CV（De-trended Coefficient of Variation）

去趋势 CV 用于衡量员工在剔除时间段货量影响后的**工作稳定性**，反映员工在相似工作负荷条件下的效率波动程度。

该指标分为两个步骤计算。

<img width="1843" height="1080" alt="5e75f21c57e602a773eaf2f07fa4ea9c" src="https://github.com/user-attachments/assets/31904582-7e8a-4e1c-a3a7-b6f2079410a9" />
  

与直接使用原始扫描量计算的 CV 不同，去趋势 CV 能更准确地反映**员工自身的稳定性**，而非系统整体货量变化造成的波动。

---

#### 三、指标组合使用说明

| 指标 | 反映内容 | 回答问题 |
|------|--------|--------|
| 相对效率 | 效率水平 | 该员工相比同公司同事，效率高还是低？ |
| 去趋势 CV | 稳定性 | 在不同时间段下，该员工的表现是否稳定？ |

两个指标结合使用，可以在劳务公司内部对员工进行更加公平、可解释的绩效分析，为人员管理、培训和排班优化提供数据支持。

---

#### 四、使用说明与范围

- 所有指标均在**劳务公司内部**进行计算，不用于跨公司直接对比  
- 时间段（Time Bin）被视为独立的工作负荷区间  
- 该指标体系适用于存在明显货量波动的作业场景

基于 **Avg Relative Efficiency（相对效率）** 与 **De-trended CV（去趋势波动性）** 的二维分析，
可以将员工在公司内部的表现划分为以下四类：

| 象限 | 条件 | 解释 | 管理含义 |
|---|---|---|---|
| I（右下） | 高效 & 稳定 | Avg > 1 且 CV 低 | 核心骨干 |
| II（左下） | 低效 & 稳定 | Avg < 1 且 CV 低 | 可培训 |
| III（左上） | 低效 & 不稳定 | Avg < 1 且 CV 高 | 风险点 |
| IV（右上） | 高效 & 不稳定 | Avg > 1 且 CV 高 | 高峰型 / 易疲劳 |

