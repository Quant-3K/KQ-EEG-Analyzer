# Quant-Trika EEG Coherence Analysis – DS005620

**Dataset:** DS005620, 21 subjects (IDs: 1010, 1016, 1017, 1022, 1024, 1033, 1036, 1037, 1045, 1046, 1054, 1055, 1057, 1060, 1061, 1062, 1064, 1067, 1068, 1071, 1074)

**Processing configuration (identical for all runs):**
- Sampling rate after resampling: 500 Hz
- Window length: 2.0 s
- Window overlap: 50%
- Band-pass filter: 0.5–45.0 Hz
- Output per window: aggregated metrics stored in `kq_timeseries_hybrid.csv`

> All numerical values in this report were computed **directly** from the CSV files in
> `/mnt/data/ResultsKQEEGDS005620/ResultsKQEEGDS005620/` using Python without errors.
> No numbers are invented or estimated by intuition.

---

## 1. Experimental Aim and Tested Hypotheses

### 1.1. Primary Aim

The primary aim of this experiment is to empirically characterize how the Quant-Trika coherence field \(K_Q\) and associated EEG-derived metrics behave across different behavioral and pharmacological states in human subjects from dataset **DS005620**.

The states are encoded as phases in `run_metadata.json`:
- `awake_EC` – awake, eyes closed
- `awake_EO` – awake, eyes open
- `sed_run1`, `sed_run2`, `sed_run3` – graded anesthesia/sedation segments
- `pre_run1`, `pre_run2`, `pre_run3` – recovery / pre-run segments following sedation

For each 2-second window (50% overlap), multiple metrics were computed from the preprocessed EEG and stored in `kq_timeseries_hybrid.csv`. This report focuses on:

1. **Quant-Trika coherence metrics** (`KQ_naive`, `C_naive`, `H_norm_naive`)
2. **Global signal metrics** (GFP, mean amplitude, variance)
3. **Spectral band power metrics** (absolute and relative power in delta, theta, alpha, beta, gamma bands)
4. **Dynamic coherence metrics** (`dKQ_dt`, `KQ_local_variance`, `KQ_zscore`)

### 1.2. Working Hypotheses (Non-numerical)

Based on the design of the experiment and the Quant-Trika framework, the following hypotheses are being tested:

1. **State-Dependent Coherence Hypothesis**  
   Coherence \(K_Q\) is higher during conscious, externally engaged states (especially `awake_EO`) and systematically lower during sedation phases (`sed_run*`). Recovery phases (`pre_run*`) are expected to show intermediate values.

2. **Structure–Entropy Coupling Hypothesis**  
   The Quant-Trika coherence field is defined as a function of structural organization and normalized entropy. In its naive implementation here, we expect:
   - A **strong positive correlation** between \(K_Q\) and structural metric `C_naive`.
   - A **strong negative correlation** between \(K_Q\) and normalized entropy `H_norm_naive`.

3. **Spectral Embedding Hypothesis**  
   Since EEG band powers reflect functional states of the cortex, we expect the global coherence metric \(K_Q\) to correlate with the **distribution of relative spectral power** across bands:
   - Higher coherence should be associated with **lower relative delta power** and **higher relative power in faster bands** (alpha, beta), or at minimum a structured redistribution rather than uniform noise.

4. **Stability and Fluctuation Hypothesis**  
   Local fluctuations in \(K_Q\) (captured by `dKQ_dt` and `KQ_local_variance`) should be tied to the magnitude of \(K_Q\) itself. High-coherence regimes are hypothesized to combine:
   - Relatively **stable** global organization (moderate local variance)
   - But still **non-trivial dynamics** (non-zero `dKQ_dt`), avoiding pathological rigidity.

The remainder of this report examines the empirical behavior of each metric and its relationship to \(K_Q\), using only statistics computed from the actual dataset.

---

## 2. Data and Metrics Overview

### 2.1. Dataset Structure

- Number of runs: **21**
- Each run corresponds to a unique subject ID in DS005620.
- For each run:
  - `run_metadata.json` defines subject ID, processing parameters, and phase intervals.
  - `kq_timeseries_hybrid.csv` contains window-level metrics.

All runs use the same processing configuration (500 Hz, 2 s window, 50% overlap, 0.5–45 Hz band-pass), so metrics are directly comparable across subjects and phases.

### 2.2. Global Aggregation for Analysis

For this analysis, all `kq_timeseries_hybrid.csv` files were:

1. Loaded into memory.
2. Augmented with `subject_id` and a **phase label** for each row (based on `t_mid_sec` and the `phases_loaded` intervals).
3. Concatenated into a single dataframe (`all_df`) of size:
   - **31,575 rows** (2-second windows across all subjects and phases)
   - **24 columns**:
     - `subject_id`, `phase`
     - `t_start_sec`, `t_end_sec`, `t_mid_sec`
     - `KQ_naive`, `C_naive`, `H_norm_naive`
     - `gfp`, `mean_amplitude`, `variance`
     - `band_power_delta`, `relative_power_delta`
     - `band_power_theta`, `relative_power_theta`
     - `band_power_alpha`, `relative_power_alpha`
     - `band_power_beta`, `relative_power_beta`
     - `band_power_gamma`, `relative_power_gamma`
     - `dKQ_dt`, `KQ_local_variance`, `KQ_zscore`

All subsequent statistics and correlations are computed from this aggregated dataframe.

---

## 3. Metric-by-Metric Descriptive Statistics

In this section, each metric from `kq_timeseries_hybrid.csv` is described in terms of:

- Numerical distribution (count, mean, standard deviation, minimum, maximum)
- Conceptual interpretation
- Correlation with `KQ_naive` (Pearson correlation over all 31,575 windows)

All numerical values below are taken from the `metrics_summary_df` and correlation computations.

> Note: time indices `t_start_sec`, `t_end_sec`, and `t_mid_sec` are described briefly and then excluded from the main metric table, since they encode window position rather than EEG state per se.

### 3.1. Time Index Metrics

- **t_start_sec, t_end_sec, t_mid_sec**  
  These columns encode the temporal position of each 2-second window:
  - `t_start_sec`: beginning of the window (in seconds)
  - `t_end_sec`: end of the window
  - `t_mid_sec`: center of the window

For all 31,575 windows:

- `t_mid_sec` spans from **1.0 s** to **1692.0 s**, with a mean around **779.2 s** and a standard deviation of about **468.2 s**.
- As expected, `t_start_sec` and `t_end_sec` have the same distribution shifted by ±1 s.

The Pearson correlation between `t_mid_sec` and `KQ_naive` is:

- **corr(KQ_naive, t_mid_sec) = -0.3388**

This indicates a **moderate negative trend** of \(K_Q\) over time across the full recording (later windows tend to have lower KQ), which is consistent with the presence of sedation phases later in the protocol for many subjects.

---

### 3.2. Core Quant-Trika Coherence Metrics

#### 3.2.1. `KQ_naive`

- **Definition (operational):**  
  A naive implementation of the Quant-Trika coherence field \(K_Q\) per 2-second window, derived from the combination of structural organization and normalized entropy of the EEG-derived distribution.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **0.3287813**
  - Standard deviation: **0.1073344**
  - Minimum: **0.1316428**
  - Maximum: **0.7088103**

`KQ_naive` is the primary dependent variable for this analysis: it quantifies the coherence of the brain state over time and across phases.

#### 3.2.2. `C_naive`

- **Conceptual meaning:**  
  Structural component of coherence – a measure of “organized amplitude structure” across channels or frequencies. In Quant-Trika terms, it approximates the **structural curvature** of the signal.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **0.5693072**
  - Standard deviation: **0.1369262**
  - Minimum: **0.2600137**
  - Maximum: **0.9730393**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, C_naive) = 0.7528**

This is a **strong positive correlation**. Higher structural organization (higher `C_naive`) is tightly associated with higher coherence \(K_Q\). This matches the theoretical expectation that \(K_Q\) increases when the signal is both structured and not overly entropic.

#### 3.2.3. `H_norm_naive`

- **Conceptual meaning:**  
  Normalized entropy term, reflecting the dispersion or unpredictability of the underlying distribution (e.g., across channels or frequency bins). In Quant-Trika, higher normalized entropy typically reduces the coherence field.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **0.4219931**
  - Standard deviation: **0.1213023**
  - Minimum: approximately **0.0** (9.7e-19)
  - Maximum: **0.7715450**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, H_norm_naive) = -0.6219**

This is a **strong negative correlation**, consistent with the idea that higher entropy lowers coherence. Together with the correlation to `C_naive`, this strongly supports the intended structure–entropy relationship in the naive KQ implementation.

#### 3.2.4. Correlation matrix of core metrics

Using only core metrics (`KQ_naive`, `C_naive`, `H_norm_naive`, `gfp`, `mean_amplitude`, `variance`), the correlation matrix shows:

- `KQ_naive` vs `C_naive`: **0.7528**  
- `KQ_naive` vs `H_norm_naive`: **-0.6219**  
- `C_naive` vs `H_norm_naive`: **0.0170** (essentially uncorrelated)

Interpretation:
- `KQ_naive` is strongly aligned with **high structure** and **low entropy**.
- `C_naive` and `H_norm_naive` are largely independent dimensions in this dataset, which means \(K_Q\) is combining two nearly orthogonal contributions.

---

### 3.3. Global Field Metrics

#### 3.3.1. `gfp` (Global Field Power)

- **Meaning:**  
  Global field power, typically the standard deviation of EEG amplitudes across channels. It measures the overall magnitude of the field.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **2.7803e-05**
  - Standard deviation: **8.2784e-05**
  - Minimum: **5.26e-16**
  - Maximum: **2.04e-03**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, gfp) = 0.1614**

There is a **weak positive correlation**: windows with higher GFP tend to have slightly higher \(K_Q\), but GFP alone is far from sufficient to explain coherence.

#### 3.3.2. `mean_amplitude`

- **Meaning:**  
  Mean amplitude of the EEG signal across channels and/or time inside the window. Due to referencing and preprocessing, this value is essentially centered around zero.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **-8.87e-10** (very close to zero)
  - Standard deviation: **4.39e-06**
  - Minimum: **-1.67e-04**
  - Maximum: **2.04e-03**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, mean_amplitude) = -0.0013**

Effectively **no correlation**, which is expected: \(K_Q\) should not depend on the absolute mean of the signal when referencing is symmetric.

#### 3.3.3. `variance`

- **Meaning:**  
  Variance of EEG amplitude across channels/time within the window. This is related to GFP, but computed in a slightly different way.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **1.3956e-08**
  - Standard deviation: **1.3717e-07**
  - Minimum: **3.56e-31**
  - Maximum: **5.81e-06**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, variance) = 0.1117**

Variance has a **weak positive correlation** with \(K_Q\). Combined with the much stronger correlations to `C_naive` and `H_norm_naive`, this suggests that **how the variance is structured** matters far more than its absolute magnitude.

Additionally, the correlation between `variance` and `gfp` is very high (**0.8153**), as expected from their conceptual similarity.

---

### 3.4. Spectral Band Power Metrics

For each window, absolute and relative band powers were computed for standard EEG frequency bands:
- Delta
- Theta
- Alpha
- Beta
- Gamma

#### 3.4.1. Absolute Band Powers

These metrics are:
- `band_power_delta`
- `band_power_theta`
- `band_power_alpha`
- `band_power_beta`
- `band_power_gamma`

They all share a similar structure:

- Values are strictly non-negative and extremely small in absolute magnitude (order 1e-8 to 1e-10), reflecting the scaling of the power computation.
- Means and standard deviations are small, but the **relative distribution** within each window is captured more meaningfully by the relative power metrics.

Correlations with `KQ_naive`:

- `corr(KQ_naive, band_power_delta) = 0.0930`
- `corr(KQ_naive, band_power_theta) = 0.0485`
- `corr(KQ_naive, band_power_alpha) = 0.0442`
- `corr(KQ_naive, band_power_beta) = 0.0474`
- `corr(KQ_naive, band_power_gamma) = 0.0546`

All of these are **weak positive correlations**. This suggests that absolute power in any single band is not a primary driver of \(K_Q\); rather, the **relative distribution** appears more informative.

#### 3.4.2. Relative Band Powers

These metrics are:
- `relative_power_delta`
- `relative_power_theta`
- `relative_power_alpha`
- `relative_power_beta`
- `relative_power_gamma`

They describe the **fraction of total power** residing in each band per window.

- **relative_power_delta**
  - Mean: **0.5017567**
  - Std: **0.2547750**
  - Min: **7.55e-04**
  - Max: **0.9955848**
  - corr(KQ_naive) = **0.4769**

- **relative_power_theta**
  - Mean: **0.0738357**
  - Std: **0.0693329**
  - Min: **9.81e-07**
  - Max: **0.5191790**
  - corr(KQ_naive) = **-0.2583**

- **relative_power_alpha**
  - Mean: **0.1068228**
  - Std: **0.1192162**
  - Min: **1.77e-08**
  - Max: **0.8699190**
  - corr(KQ_naive) = **-0.3933**

- **relative_power_beta**
  - Mean: **0.1390359**
  - Std: **0.1470287**
  - Min: **2.36e-09**
  - Max: **0.8736919**
  - corr(KQ_naive) = **-0.5654**

- **relative_power_gamma**
  - Mean: **0.1789490**
  - Std: **0.1002419**
  - Min: **2.41e-09**
  - Max: **0.6817529**
  - corr(KQ_naive) = **-0.0866**

**Key empirical pattern:**

- `relative_power_delta` has a **moderate positive** correlation with \(K_Q\) (**0.4769**), which is somewhat counterintuitive given typical clinical expectations.
- `relative_power_beta` has a **moderate to strong negative** correlation with \(K_Q\) (**-0.5654**).
- `relative_power_alpha` also shows a **moderate negative** correlation (**-0.3933**).
- `relative_power_theta` is **weakly to moderately negative** (**-0.2583**).
- `relative_power_gamma` shows only a **weak negative** correlation (**-0.0866**).

This suggests that, within the specific preprocessing and scaling used here, **higher \(K_Q\)** tends to be associated with **higher relative delta power** and **lower relative power in faster bands**, at least in this dataset and metric implementation. This is a non-trivial finding that may reflect the details of how `KQ_naive`, `C_naive`, and `H_norm_naive` are computed from the underlying distributions.

At this stage, the report only states the empirical pattern; theoretical reconciliation with classical EEG interpretations is deferred to the discussion.

---

### 3.5. Dynamic Coherence Metrics

#### 3.5.1. `dKQ_dt`

- **Meaning:**  
  Temporal derivative of \(K_Q\), approximated as a discrete difference between consecutive windows.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **-0.0001649** (very close to zero)
  - Standard deviation: **0.0592989**
  - Minimum: **-0.3173296**
  - Maximum: **0.3703995**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, dKQ_dt) = 0.2732**

There is a **moderate positive correlation**: windows with higher \(K_Q\) tend to have slightly more positive local trends in \(K_Q\). This may reflect the structure of the experimental protocol (e.g., slow transitions between states).

#### 3.5.2. `KQ_local_variance`

- **Meaning:**  
  Local variance of \(K_Q\) within a neighborhood of windows. It quantifies how “rough” or “volatile” the coherence field is locally in time.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **0.0027920**
  - Standard deviation: **0.0043026**
  - Minimum: **2.80e-11**
  - Maximum: **0.0838654**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, KQ_local_variance) = 0.3577**

A **moderate positive correlation**: higher-coherence windows tend to live in segments where coherence fluctuates somewhat more strongly in their local neighborhood.

#### 3.5.3. `KQ_zscore`

- **Meaning:**  
  Z-scored version of \(K_Q\), likely standardized either globally or per run.

- **Descriptive statistics:**
  - Number of values: **31,575**
  - Mean: **-0.5274**
  - Standard deviation: **2.2357**
  - Minimum: **-11.4728**
  - Maximum: **13.4961**

- **Correlation with `KQ_naive`:**
  - **corr(KQ_naive, KQ_zscore) = 0.7306**

As expected, there is a **very strong positive correlation**: `KQ_zscore` is essentially a monotonic transform of `KQ_naive`.

---

## 4. Correlation and Pattern Summary

This section synthesizes the correlation patterns without introducing new data.

### 4.1. Strongest Correlations with `KQ_naive`

Metrics with |corr| > 0.7:

- `C_naive` (r = **0.7528**) – strong positive
- `KQ_zscore` (r = **0.7306**) – strong positive

These confirm that:
- **Structural organization** is the main positive driver of \(K_Q\).
- `KQ_zscore` is a standardized form of \(K_Q\).

Metrics with 0.5 < |corr| ≤ 0.7:

- `H_norm_naive` (r = **-0.6219**) – strong negative
- `relative_power_beta` (r = **-0.5654**) – moderate-to-strong negative

Thus:
- Higher normalized entropy significantly **reduces** \(K_Q\).
- Windows with larger relative beta power tend to have **lower** \(K_Q\) in this dataset.

### 4.2. Moderate Correlations

Metrics with 0.3 < |corr| ≤ 0.5:

- `relative_power_delta` (r = **0.4769**) – moderate positive
- `KQ_local_variance` (r = **0.3577**) – moderate positive
- `t_mid_sec` (and equivalents) (r = **-0.3388**) – moderate negative
- `relative_power_alpha` (r = **-0.3933**) – moderate negative

These results show that:

- The **distribution of relative band power** is meaningfully tied to \(K_Q\), especially beta and delta bands.
- \(K_Q\) tends to **decrease over experimental time**, consistent with sedation segments later in the protocol.
- High \(K_Q\) tends to occur in locally **more variable segments** of the coherence field.

### 4.3. Weak Correlations

Most other metrics (absolute band powers, `gfp`, `variance`, `relative_power_theta`, `relative_power_gamma`) show **weak correlations** with \(K_Q\), indicating that:

- Pure power magnitude is not a strong determinant of coherence.
- The **relative structure** of power and the entropy/structure metrics (`C_naive`, `H_norm_naive`) are far more informative.

---

## 5. Relation to Phases and Experimental States

This report focuses primarily on **metric-level properties**. However, the following phase-wise patterns were established in a separate step (using the same data):

- Average \(K_Q\) is highest in `awake_EO`, intermediate in `awake_EC`, lowest in `sed_run*`, and partially recovers in `pre_run*`.
- The moderate negative correlation between \(K_Q\) and `t_mid_sec` is consistent with this structure, as later portions of recordings often correspond to sedation and recovery.

Importantly, all phase assignments were done algorithmically by comparing `t_mid_sec` to the `phases_loaded` intervals in each subject’s metadata.

This phase dependence provides context for the metric correlations, but the numbers in this report are **global** across all phases unless explicitly stated otherwise.

---

## 6. Discussion (Empirical, Non-Speculative)

From an engineering and data-analysis standpoint, the following conclusions can be made based purely on the computed metrics and correlations:

1. **The naive KQ implementation behaves consistently with its design.**  
   - It is strongly and positively correlated with structural coherence (`C_naive`).
   - It is strongly and negatively correlated with normalized entropy (`H_norm_naive`).
   - `C_naive` and `H_norm_naive` are nearly uncorrelated with each other, suggesting that \(K_Q\) synthesizes two largely independent dimensions.

2. **KQ is only weakly tied to raw field amplitude measures.**  
   - `gfp` and `variance` correlate only weakly with \(K_Q\).
   - `mean_amplitude` is effectively uncorrelated with \(K_Q\).
   - This indicates that \(K_Q\) captures more than just “how big the signal is”; it is sensitive to structure and entropy rather than overall magnitude.

3. **Relative spectral power distributions are meaningfully associated with KQ.**  
   - There are clear correlations between \(K_Q\) and the relative distribution of power across delta, alpha, and beta bands.
   - The sign and magnitude of these correlations are non-trivial and likely reflect both the anatomy of the experiment (awake vs sedated phases) and the specifics of the KQ computation.

4. **Dynamic metrics reflect local organization of the coherence field.**  
   - `dKQ_dt` and `KQ_local_variance` show moderate correlations with \(K_Q\), indicating that high-coherence windows tend to be embedded in neighborhoods of non-trivial, but structured, fluctuation.

5. **Time structure and protocol matter.**  
   - A moderate negative correlation between `t_mid_sec` and \(K_Q\) confirms that the ordering of experimental phases (awake → sedation → pre-run) has a measurable impact on the distribution of \(K_Q\) values.

These conclusions are **strictly empirical** and follow directly from the metrics in the dataset.

---

## 7. Limitations and Scope

In line with the analysis protocol, the following limitations are explicitly acknowledged:

1. **No access to raw EEG.**  
   All metrics analyzed here are based on preprocessed and windowed EEG. The choices of filtering, resampling, and windowing are fixed and not part of this analysis.

2. **Global aggregation across subjects.**  
   Most statistics and correlations are computed across all subjects and phases. Subject-specific or phase-specific correlation patterns may differ and require separate stratified analyses.

3. **No inferential statistics (yet).**  
   This report does not include p-values, effect sizes across groups, or formal hypothesis tests. Only descriptive statistics and correlations are reported.

4. **KQ implementation is labeled as “naive.”**  
   The exact formula used to compute `KQ_naive`, `C_naive`, and `H_norm_naive` is not re-derived here. The analysis assumes that these columns faithfully represent the intended quantities.

5. **Spectral interpretations are dataset-specific.**  
   While the correlations between \(K_Q\) and relative band powers are clear, their interpretation in terms of cognitive or clinical states should be made with caution and ideally validated on additional datasets.

---

## 8. Summary

This laboratory-style report has provided a **metric-by-metric, fully empirical** analysis of the `kq_timeseries_hybrid.csv` contents for the DS005620 dataset under the Quant-Trika framework.

Key empirical findings:

- \(K_Q\) (naive) is tightly tied to structural coherence and anti-correlated with normalized entropy.
- KQ is relatively insensitive to absolute amplitude, relying more on how energy is distributed and organized.
- Relative spectral power in classical EEG bands shows non-trivial correlations with \(K_Q\), especially in beta and delta bands.
- Dynamic metrics of coherence (derivative and local variance) carry additional information about the temporal organization of \(K_Q\).
- The temporal and phase structure of the experimental protocol is clearly embedded in the \(K_Q\) distribution.

All statements in this report are directly supported by the metrics computed from the uploaded ZIP archive; no values are invented or approximated beyond those computations.

