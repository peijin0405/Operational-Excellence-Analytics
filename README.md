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

<img width="1706" height="1026" alt="5d5d252c313b32c0405afd7a2f0cd3c4" src="https://github.com/user-attachments/assets/567610d4-5657-4e14-a44e-c7d2575c982c" />
  

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
