## 📊 Metrics Definition

This project evaluates individual productivity using **volume-normalized efficiency metrics** to ensure fair comparison under fluctuating workloads.

---

### 1. Relative Efficiency (Normalized Efficiency)

**Relative Efficiency** measures an employee’s productivity **relative to the average productivity within the same labor company and the same time bin**, removing the effect of system-level volume fluctuations.


<img width="1505" height="621" alt="2f1f00d34ad9269df698c2c73060b5c4" src="https://github.com/user-attachments/assets/587c46ec-4400-42fc-bf7f-72dd244c7704" />


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
