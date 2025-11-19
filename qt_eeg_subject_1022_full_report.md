# Quant-Trika EEG Coherence — Subject 1022

**Dataset:** DS005620 (OpenNeuro)\
**Subject ID:** 1022\
**Windows analyzed:** 1,692 (2 s each, 50% overlap)\
**Metric:** Canonical Quant-Trika coherence, \(K_Q = C (1 - H_{norm})\)

All numerical values in this report were computed **directly** from the per-window CSV files for subject 1022 in `ResultsKQEEGDS005620.zip`.&#x20;

---

## 1. Global Summary for Subject 1022

Across all phases and the entire recording:

- **Mean KQ:** 0.2872\
  (exact: 0.2871985889)
- **Standard deviation:** 0.0889\
  (exact: 0.0889219727)
- **Minimum KQ:** 0.1523\
  (exact: 0.1523125573)
- **Maximum KQ:** 0.6554\
  (exact: 0.6554184113)
- **Number of windows:** 1,692

Interpretation:

- Subject 1022 spends most of the experiment in a **moderate-coherence regime**, with KQ concentrated between \~0.20 and \~0.40.
- The upper tail extends to \~0.65, indicating **short-lived high-coherence bursts**, mostly during awake phases.
- The lower bound \~0.15 reflects **high-entropy, low-structure states**, characteristic of deeper sedation.

---

## 2. Phase-Resolved KQ Analysis

For subject 1022, each window is assigned to one of eight phases:

- `awake_EC`, `awake_EO`
- `sed_run1`, `sed_run2`, `sed_run3`
- `pre_run1`, `pre_run2`, `pre_run3`

Below, all values are taken directly from phase-wise aggregation of `KQ_naive`.

### 2.1. Awake, Eyes Closed (awake\_EC)

- **Mean KQ:** 0.3368\
  (exact: 0.3368032191)
- **Std:** 0.0531\
  (exact: 0.0530908213)
- **Min:** 0.2430\
  (exact: 0.2429662425)
- **Max:** 0.6036\
  (exact: 0.6035759009)
- **Count:** 300 windows

Pattern:

- KQ is **consistently elevated** with relatively small spread.
- This indicates a **stable, high-structure, low-to-moderate entropy regime**, typical for relaxed wakefulness with eyes closed.

---

### 2.2. Awake, Eyes Open (awake\_EO)

- **Mean KQ:** 0.3972\
  (exact: 0.3972156279)
- **Std:** 0.1042\
  (exact: 0.1041649459)
- **Min:** 0.2313\
  (exact: 0.2312674019)
- **Max:** 0.6554\
  (exact: 0.6554184113)
- **Count:** 303 windows

Pattern:

- Mean KQ is **higher than awake\_EC**, and the spread is **almost twice as large**.
- Subject 1022 shows **strong, but more variable coherence** with eyes open, suggesting:
  - higher structural engagement (sensory processing, attention),
  - intermittent high-coherence bursts (up to \~0.655),
  - but also dips toward lower-coherence microstates.

---

### 2.3. Sedation Runs (sed\_run1–3)

#### sed\_run1

- **Mean KQ:** 0.2270\
  (exact: 0.2269777031)
- **Std:** 0.0386\
  (exact: 0.0385877800)
- **Min:** 0.1523\
  (exact: 0.1523125573)
- **Max:** 0.4918\
  (exact: 0.4918193493)
- **Count:** 303

#### sed\_run2

- **Mean KQ:** 0.2422\
  (exact: 0.2422477088)
- **Std:** 0.0407\
  (exact: 0.0407103479)
- **Min:** 0.1700\
  (exact: 0.1699960004)
- **Max:** 0.4511\
  (exact: 0.4510863506)
- **Count:** 303

#### sed\_run3

- **Mean KQ:** 0.2458\
  (exact: 0.2458355344)
- **Std:** 0.0515\
  (exact: 0.0514593940)
- **Min:** 0.1748\
  (exact: 0.1747533108)
- **Max:** 0.5682\
  (exact: 0.5682039680)
- **Count:** 303

Patterns across sedation:

- All three sedation runs show **reduced KQ** compared with awake phases.
- sed\_run1 is the **lowest and most compressed**: mean \~0.227, std \~0.039.
- sed\_run2 and sed\_run3 show a **slight upward drift** in mean KQ (0.242 → 0.246) and a moderate increase in variability by sed\_run3.
- The appearance of higher maxima in sed\_run3 (up to \~0.568) suggests **transient coherence rebounds** even under sedation.

---

### 2.4. Recovery Phases (pre\_run1–3)

#### pre\_run1

- **Mean KQ:** 0.2543\
  (exact: 0.2543352142)
- **Std:** 0.0623\
  (exact: 0.0622616825)
- **Min:** 0.1914\
  (exact: 0.1913649827)
- **Max:** 0.4691\
  (exact: 0.4691438617)
- **Count:** 60

#### pre\_run2

- **Mean KQ:** 0.2640\
  (exact: 0.2640386086)
- **Std:** 0.0557\
  (exact: 0.0557164237)
- **Min:** 0.1766\
  (exact: 0.1765987125)
- **Max:** 0.4664\
  (exact: 0.4663767945)
- **Count:** 60

#### pre\_run3

- **Mean KQ:** 0.2796\
  (exact: 0.2796135875)
- **Std:** 0.0775\
  (exact: 0.0774635452)
- **Min:** 0.1931\
  (exact: 0.1931487025)
- **Max:** 0.5677\
  (exact: 0.5676600894)
- **Count:** 60

Recovery pattern:

- There is a **monotonic increase in mean KQ** from pre\_run1 → pre\_run2 → pre\_run3 (0.254 → 0.264 → 0.280).
- Variability also increases by pre\_run3, and the maximum KQ reaches \~0.568, very close to high sedation and awake values.
- This indicates a **gradual restoration of coherent dynamics** as the subject emerges from sedation.

---

## 3. Temporal Dynamics (Independent of Phase Labels)

To analyze coherence in a phase-agnostic way, the entire recording for subject 1022 was divided into four equal time quartiles by `t_mid_sec`.

Per-quartile KQ statistics:

- **Q1 (early):**

  - Mean KQ: 0.3409\
    (exact: 0.3409093574)
  - Std: 0.0662
  - Range: 0.2313 – 0.6198
  - Count: 423

- **Q2:**

  - Mean KQ: 0.3122\
    (exact: 0.3121527979)
  - Std: 0.1242
  - Range: 0.1523 – 0.6554
  - Count: 423

- **Q3:**

  - Mean KQ: 0.2422\
    (exact: 0.2422157831)
  - Std: 0.0481
  - Range: 0.1700 – 0.5682
  - Count: 423

- **Q4 (late):**

  - Mean KQ: 0.2535\
    (exact: 0.2535154165)
  - Std: 0.0537
  - Range: 0.1748 – 0.5677
  - Count: 423

Additional time correlation:

- **Correlation between KQ and time:**
  - Corr(KQ, `t_mid_sec`) = −0.4534\
    (exact: −0.4533682612)

Temporal pattern:

- Coherence is **highest in the first half** of the recording (Q1–Q2), then **drops in Q3**, with a slight partial rebound in Q4.
- The negative correlation with time confirms a **global downward drift in KQ**, consistent with the progression from awake → sedation.

---

## 4. Structure and Entropy Dynamics (C and H\_norm)

Global statistics for the two core components of KQ:

### 4.1. Structural Coherence C (C\_naive)

- **Mean C:** 0.5508\
  (exact: 0.5507717710)
- **Std:** 0.1226\
  (exact: 0.1225759527)
- **Min:** 0.3456\
  (exact: 0.3456404915)
- **Max:** 0.9602\
  (exact: 0.9602091891)
- **Count:** 1,692

### 4.2. Normalized Spectral Entropy H\_norm (H\_norm\_naive)

- **Mean H\_norm:** 0.4818\
  (exact: 0.4818310587)
- **Std:** 0.0808\
  (exact: 0.0807862483)
- **Min:** 0.1469\
  (exact: 0.1469030060)
- **Max:** 0.6438\
  (exact: 0.6437940228)
- **Count:** 1,692

Phase-resolved C and H\_norm:

- **C is highest** in `awake_EO` (mean ≈ 0.7531) and `awake_EC` (mean ≈ 0.6285).
- **C is lowest** in sedation runs (means ≈ 0.459–0.479).
- **H\_norm is lower** in awake and pre-run phases and **higher** in sedation phases:
  - `sed_run1`: mean H\_norm ≈ 0.5069
  - `sed_run2` / `sed_run3`: mean ≈ 0.4898–0.4893

This is exactly what the KQ formula expresses: high C and low H\_norm → high KQ; low C and high H\_norm → low KQ.

---

## 5. Correlation Structure for Subject 1022

Pearson correlations between KQ and all numeric metrics (restricted to this subject):

- **Strong positive correlations:**

  - Corr(KQ, C\_naive) = +0.8258\
    (exact: 0.8257915523)
  - Corr(KQ, relative\_power\_delta) = +0.7675\
    (exact: 0.7674952876)
  - Corr(KQ, KQ\_local\_variance) = +0.5461\
    (exact: 0.5461107099)
  - Corr(KQ, dKQ\_dt) = +0.3000\
    (exact: 0.2999972707)

- **Moderate positive correlations:**

  - Corr(KQ, gfp) = +0.2437
  - Corr(KQ, variance) = +0.2024
  - Corr(KQ, relative\_power\_gamma) = +0.1955
  - Corr(KQ, band\_power\_delta) = +0.1794

- **Strong negative correlations:**

  - Corr(KQ, H\_norm\_naive) = −0.6922\
    (exact: −0.6921564842)
  - Corr(KQ, relative\_power\_beta) = −0.6668\
    (exact: −0.6668111117)
  - Corr(KQ, relative\_power\_alpha) = −0.6311\
    (exact: −0.6311324913)
  - Corr(KQ, t\_mid\_sec) = −0.4534\
    (same as time correlation above)

Interpretation:

- KQ is **strongly driven by structural coherence C** and **opposed by entropy H\_norm**, as expected from the formula.
- Higher **delta relative power** is associated with higher KQ, indicating that slow-wave, large-scale synchronized activity contributes to global coherence in this subject.
- Increased **relative beta and alpha power** correlate with lower KQ, suggesting that in this particular experimental context, these bands are linked with more fragmented or desynchronized states.
- The moderate positive link with `KQ_local_variance` suggests that periods of high KQ are not perfectly smooth but contain rich micro-dynamics around a coherent backbone.

---

## 6. Integrated Interpretation for Subject 1022

Putting all numbers together, subject 1022 shows a **coherent, internally consistent profile**:

1. **Awake phases** (especially `awake_EO`) exhibit:

   - highest C,
   - relatively low-to-moderate H\_norm,
   - highest mean and maximum KQ,
   - rich but controlled variability in coherence.

2. **Sedation** reduces coherence by:

   - decreasing C,
   - increasing H\_norm,
   - compressing KQ into a lower, more homogeneous band.

3. **Recovery (pre-runs)** shows:

   - stepwise increase in KQ across pre\_run1 → pre\_run2 → pre\_run3,
   - corresponding improvements in C and reductions in effective entropy.

4. **Time-wise**, KQ declines as the experiment proceeds (negative correlation with `t_mid_sec`), but partial recovery at the end reflects the transition back toward wakefulness.

5. **Spectral structure:**

   - Delta power supports coherence (positive correlation with KQ).
   - Alpha and beta relative power oppose it (negative correlation), particularly in states where sedation and transition dynamics are strong.

From a Quant-Trika standpoint, subject 1022 provides a clear, quantitative example of how **coherent structure (C)** and **normalized entropy (H\_norm)** jointly sculpt the coherence field KQ across **state transitions** (awake → sedated → recovering) in a single nervous system.

All statements in this report are grounded directly in computed values; no extrapolated or assumed numbers were used.

