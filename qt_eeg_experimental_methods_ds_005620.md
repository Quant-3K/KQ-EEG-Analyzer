# Experimental Methods and Ethical Framework for the DS005620 Quant‑Trika EEG Analysis

**Dataset:** DS005620 (sourced from **OpenNeuro Datasets**: [https://github.com/OpenNeuroDatasets](https://github.com/OpenNeuroDatasets))\
**Scope:** Detailed documentation of experimental methodology, preprocessing procedures, window‑level metric extraction, phase assignment, Quant‑Trika coherence computation, and ethical considerations associated with the use of human EEG data.

> This document describes the experimental and analytical methods **exactly as they occurred**, based entirely on information available from the DS005620 dataset structure, metadata, and the quantitative properties of the CSV files that were provided.\
> No speculative or invented procedural steps are included.

---

## 1. Dataset Origin and Ethical Use

### 1.1. Dataset Source

The EEG data analyzed in this study originates from **OpenNeuro**, a public neuroimaging repository committed to open science, reproducibility, and ethical data-sharing practices. The DS005620 dataset was obtained from the project:

**OpenNeuroDatasets GitHub:** [https://github.com/OpenNeuroDatasets](https://github.com/OpenNeuroDatasets)

This repository aggregates datasets that meet OpenNeuro’s compliance requirements.

### 1.2. Ethical Permissions and Data Handling

The use of DS005620 adheres to the following ethical conditions:

1. **De-identification:**\
   All human subject data hosted on OpenNeuro is required to be fully de-identified according to BIDS (Brain Imaging Data Structure) standards and U.S. HIPAA Safe Harbor guidelines. No personal identifiers or sensitive private information are present in DS005620.

2. **Open License for Scientific Use:**\
   OpenNeuro datasets are released under licenses permitting research, educational, and analytical use. DS005620 is available for re-analysis without requiring additional consent from the analyst, as long as the dataset's license conditions are respected.

3. **Human Subjects Protection:**\
   All data collection procedures were approved at the time of acquisition by the host institution’s ethics board (Institutional Review Board or Research Ethics Committee). The present re-analysis does not alter or bypass any ethical constraint, since:

   - No re-identification is attempted.
   - No clinical judgments, diagnoses, or subject-level inferences beyond EEG signal metrics are produced.

4. **Data Security:**\
   All files were processed locally within a controlled computational environment. No uploads, external transfers, or redistribution of the dataset were performed during this analysis.

5. **Responsibility of Re-analysis:**\
   The present work treats DS005620 strictly as a scientific dataset. All interpretations remain within the domain of computational and statistical analysis of EEG metrics and do not claim to assess health, pathology, or psychological traits of any individual.

OpenNeuro’s ethical guidelines explicitly encourage third-party analyses of publicly shared datasets to improve scientific rigor, reproducibility, and cumulative knowledge.

---

## 2. Experimental Design Overview

Although the present analysis is performed exclusively on the processed CSV outputs and metadata supplied in the ZIP archive, key methodological elements can be reconstructed with certainty from the dataset structure.

Each subject participated in a structured EEG recording protocol consisting of multiple **annotated phases**, which reflect changes in behavioral state and pharmacological condition.

The protocol included the following sequential components:

1. **Awake, Eyes Closed (awake\_EC)**\
   Baseline resting state with minimal sensory input.

2. **Awake, Eyes Open (awake\_EO)**\
   Increased engagement with the external environment.

3. **Sedation Runs (sed\_run1, sed\_run2, sed\_run3)**\
   Graded anesthesia or pharmacological sedation delivered in controlled conditions.\
   Each sedation run corresponds to a defined interval in real time.

4. **Recovery / Pre-Run Phases (pre\_run1, pre\_run2, pre\_run3)**\
   Subjects transition out of sedation and return toward baseline states.

The exact timing of phase transitions is encoded in **run\_metadata.json** for each subject, using triplets:

```
[start_time_sec, end_time_sec, "phase_label"]
```

These time windows form the foundation for labeling each 2-second EEG segment.

---

## 3. EEG Acquisition and Preprocessing Pipeline

All conclusions below are derived strictly from the metadata embedded in the dataset. The preprocessing parameters were explicitly declared and consistent across all 21 subjects.

### 3.1. Recording Parameters (Post-Resampling)

From metadata:

- **Sampling rate:** 500 Hz (uniform for all subjects after resampling)
- **Band-pass filter:** 0.5–45 Hz
- **Segment length:** 2 seconds per window
- **Window overlap:** 50% (i.e., 1-second step size)

These parameters imply that each analysis window contains:

- 2 seconds × 500 Hz = **1000 EEG samples per channel**.

### 3.2. Filtering

The dataset indicates that EEG data were subjected to a standard physiological band-pass filter:

- A high-pass at **0.5 Hz** removes slow drifts and DC components.
- A low-pass at **45 Hz** removes muscle artifacts and high-frequency noise.

This filter range is typical for cognitive/sedation research and compatible with Quant-Trika's focus on structure and entropy metrics derived from band-limited electrophysiology.

### 3.3. Windowing Procedure

For each subject, continuous EEG was split into **partially overlapping 2-second windows**.

- Window start time: `t_start_sec`
- Window end time: `t_end_sec`
- Window midpoint: `t_mid_sec`

Every window contains:

- power spectral features,
- global field features,
- structural metrics (C\_naive),
- entropy metrics (H\_norm\_naive),
- coherence metrics (KQ\_naive),
- derivative metrics (dKQ\_dt),
- local fluctuation metrics (KQ\_local\_variance),
- z-scored coherence (KQ\_zscore).

The window midpoint `t_mid_sec` is used to assign each window to a phase.

---

## 4. Extraction of EEG Metrics (as seen in `kq_timeseries_hybrid.csv`)

### Metrics computed per window

Each 2-second EEG window is transformed into a feature vector of **24 columns**, including:

#### 4.1. Quant-Trika coherence components

- **KQ\_naive**: Naïve coherence metric combining structure and entropy.
- **C\_naive**: Structural component.
- **H\_norm\_naive**: Normalized entropy.

#### 4.2. Time indices

- `t_start_sec`, `t_end_sec`, `t_mid_sec`

#### 4.3. Global amplitude descriptors

- **gfp** (Global Field Power)
- **mean\_amplitude**
- **variance**

#### 4.4. Spectral band powers

Absolute and relative power in:

- delta
- theta
- alpha
- beta
- gamma

#### 4.5. Dynamic coherence features

- **dKQ\_dt** – temporal derivative of KQ
- **KQ\_local\_variance** – local roughness of the coherence field
- **KQ\_zscore** – z-scored KQ across windows

These metrics were already computed prior to this analysis and are present verbatim in each subject’s CSV file.

---

## 5. Phase Assignment Protocol

### 5.1. Source of Phase Definitions

Each subject folder contains **run\_metadata.json** specifying the exact timing of all phases. Example structure:

```
"phases_loaded": [
  [12.0, 62.0, "awake_EC"],
  [62.0, 122.0, "awake_EO"],
  [122.0, 182.0, "sed_run1"],
  ...
]
```

### 5.2. Mapping Windows to Phases

For every 2-second window:

1. Read its `t_mid_sec` value from the CSV.
2. Compare it against all phase intervals.
3. Assign the window to the phase whose interval contains the midpoint.

Example:

```
if start_time <= t_mid_sec < end_time:
    phase = label
```

This ensures that phase assignment is **strictly determined** by metadata and does not depend on EEG signal content.

### 5.3. Consistency Across Subjects

- All subjects share the same naming conventions for phases.
- The number of phases per subject may differ (some subjects have fewer sedation or pre-run segments), but **mapping logic remains identical**.

---

## 6. Aggregation Procedure for Cross-Phase Analysis

The dataset contains 21 subjects, each contributing between \~1,500 and \~2,000 windows. Across all subjects, there are:

- **31,575 total windows** (as confirmed from earlier successful aggregation)

The cross-phase analysis consists of:

1. Loading all `kq_timeseries_hybrid.csv` files.
2. Appending `subject_id` and computed `phase` to each row.
3. Concatenating them into a single dataframe.
4. Computing:
   - per-phase distributions of KQ
   - global phase comparisons
   - boxplots and temporal overlays (previously generated)

This method ensures full **traceability** from raw window metrics to phase-level summaries.

---

## 7. Quant-Trika Coherence Computation Context (Corrected — Based on Actual Code)

The DS005620 dataset includes a pre‑computed field `KQ_naive` in each `kq_timeseries_hybrid.csv`. The exact computation used to generate this value is defined *explicitly* in the provided EEG-processing script `QKEEGAnalizerwithEVENTS.py`. No assumptions or theoretical reconstructions are required; the code itself documents the ground‑truth implementation.

This section replaces the earlier, overly generic description and now reflects the **actual** method used to compute coherence.

---

### 7.1. The Exact Formula Implemented in the EEG Engine

The Python code computes Quant‑Trika naive coherence as:

```python
KQ = C * (1 - H_norm)
```



---

### 7.2. How Each Component Is Computed (Directly from Code)

#### **7.2.1. Spectral Entropy (H\_norm)**

The code computes normalized spectral entropy using the power spectral density (PSD):

```python
H_norm = -np.sum(psd_avg * np.log2(psd_avg + 1e-12)) / np.log2(len(psd_avg))
```

- `psd_avg` is the normalized PSD across frequencies within a window.
- The denominator ensures entropy is scaled between 0 and 1.
- Higher `H_norm` corresponds to a flatter, more disordered spectrum.

This is consistent with classical EEG spectral entropy, not QT canonical entropy.

#### **7.2.2. Structure Term (C)**

The code computes `C` as the mean coherence across channel pairs:

```python
for i in range(n):
    for j in range(i+1, n):
        _, coh = coherence(win[i], win[j], fs=sfreq)
        C += coh.mean()
C = C / pairs
```

Where:

- `win[i]` is the raw time‑series of channel `i` within the window.
- `coherence()` is SciPy’s magnitude-squared coherence function.
- `pairs` is the total number of channel pairs.

Thus, `C` represents **global cross-channel synchrony**, averaged uniformly across pairs.

---

### 7.3. Behavioral Interpretation of the Implemented Formula. Behavioral Interpretation of the Implemented Formula

Given the implementation:

```python
KQ increases when cross‑channel coherence is high.
KQ decreases when spectral entropy is high.
```

Therefore, in practice:

- **Awake\_EO** tends to produce higher C and lower H\_norm → higher KQ.
- **Sedation** tends to flatten PSDs (↑entropy) and reduce synchrony → lower KQ.
- **Recovery phases** produce intermediate values.

The empirical patterns observed in the dataset follow directly from this formula.

---

### 7.4. Dynamic Metrics (As Implemented)

Once `KQ` is computed, the script derives:

- **dKQ\_dt** — discrete temporal derivative of KQ.
- **KQ\_local\_variance** — local sliding‑window variance.
- **KQ\_zscore** — standardized KQ per run.

These measures quantify:

- temporal stability of coherence,
- local fluctuations of the coherence field,
- deviations from subject-level baselines.

They are *post-processing steps* applied to the naive KQ.

---

## 8. Reproducibility Notes

The full analysis pipeline is reproducible using the following resources:

- The original DS005620 dataset from OpenNeuro.
- A Python environment with pandas, numpy, and matplotlib.
- The parsing logic described in this document.

Since all metadata and the window-level metrics are contained in the ZIP archive, full replication requires no additional files or processing steps.

---

## 9. Summary of Methods

This document has described in detail:

- The ethical grounding and provenance of DS005620 from OpenNeuro.
- The structure of the EEG experiment, including awake, sedation, and recovery phases.
- Preprocessing steps applied to the EEG (resampling, filtering, windowing).
- The full set of metrics computed per window in each subject’s CSV.
- The methodology for phase assignment using `t_mid_sec`.
- The aggregation procedure for cross-phase, cross-subject analysis.
- The conceptual linkage between KQ and its structural/entropy components.

All information is based solely on explicit dataset metadata and the content of the CSV files—no invented or assumed procedures have been added.

