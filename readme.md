# Quant‑Trika EEG Coherence Analysis — DS005620

This repository contains a complete, end‑to‑end analysis of EEG coherence using the **Quant‑Trika** framework, based on the publicly available human EEG dataset **DS005620** from OpenNeuro. The goal of this repository is to provide a fully transparent, reproducible, and methodologically rigorous implementation of the Quant‑Trika coherence metric applied to real EEG data.

The repository includes:

- **Three detailed analytical reports** (Methods, Phase‑resolved Results, and Full Experimental Interpretation)
- **A ZIP archive** with all computed window‑level metrics (`KQ`, `C`, `H_norm`, spectral features, derivatives, etc.)
- **The original analysis engine** (`QKEEGAnalizerwithEVENTSComplete.py`) used to compute the metrics

Together, these materials document the full workflow—from data origin and preprocessing to metric extraction, phase assignment, coherence computation, and interpretation.

---

## 📁 Repository Structure

```
/README.md                         ← You are here
/ResultsKQEEGDS005620.zip          ← All computed EEG window metrics
/QKEEGAnalizerwithEVENTSComplete.py        ← Python script used to generate KQ, C, H_norm, etc.

/reports/
    QT-EEG_Experimental_Methods_DS005620.md
    QT-EEG_Phase_Resolved_KQ_Report_DS005620.md
    QT-EEG_Full_Analysis_and_Interpretation.md   (if included)
```

Each report is self‑contained and written for different levels of analysis depth.

---

# 1. What This Repository Demonstrates

### ✅ **1. Application of canonical Quant‑Trika coherence (KQ) to real EEG data**

This repository implements the canonical Quant‑Trika coherence formula:

```
KQ = C * (1 − H_norm)
```


- `C` — structural synchrony (mean cross‑channel coherence)
- `H_norm` — normalized spectral entropy

This combination measures how much information is structured vs. disordered in the EEG signal.

### ✅ **2. Phase‑dependent behavior of brain coherence**

Using the metadata from the dataset, each EEG window is mapped into functional states:

- Awake, eyes closed
- Awake, eyes open
- Sedation (run1–run3)
- Recovery (pre‑run1–pre‑run3)

The analysis reveals:

- Higher KQ during awake states (especially eyes‑open)
- Lower KQ during sedation (entropy ↑, structure ↓)
- Partial recovery during post‑sedation phases

These patterns emerge **directly from the data**, without assumptions.

### ✅ **3. Fully transparent, step‑by‑step scientific workflow**

The analysis follows strict principles:

- No invented values
- All metrics computed directly from the ZIP contents
- Python code validated at each stage
- Empirical data strictly separated from interpretation

This ensures full scientific reproducibility.

---

# 2. Contents of the Repository

## 📄 **1. Experimental Methods Report**

**Filename:** `QT-EEG_Experimental_Methods_DS005620.md`

This document describes:

- Dataset origin and ethics
- Experimental protocol
- EEG preprocessing (filtering, windowing, resampling)
- Extraction of KQ, C, H\_norm, spectral features
- Phase assignment via `t_mid_sec`
- Aggregation procedures

It reflects exactly what the EEG engine does—no assumptions, no gaps.

---

## 📄 **2. Phase‑Resolved Coherence Report**

**Filename:** `QT-EEG_Phase_Resolved_KQ_Report_DS005620.md`

This report contains:

- Phase‑by‑phase KQ statistics across all subjects
- Mean, variance, min, max for each phase
- Empirical comparisons between awake, sedation, and recovery
- Interpretation within Quant‑Trika

This is the main reference for understanding EEG state transitions in terms of coherence.

---

## 📄 **3. Full Experiment Interpretation (optional third report)**

If provided, this report synthesizes:

- Methods
- Phase analysis
- Cross‑subject comparison
- Interpretations anchored in Quant‑Trika computational ontology

---

## 📦 **4. ZIP Archive: Window‑Level EEG Metrics**

**Filename:** `ResultsKQEEGDS005620.zip`

Inside the ZIP you will find:

- All per‑window CSV files (24 columns each)
- Plots generated during the pipeline
- Per‑subject folders containing KQ, C, H\_norm, spectral bands, dynamic metrics

This archive is the raw material for all statistical analysis.

---

## 🧠 **5. EEG Analysis Engine**

**File:** `QKEEGAnalizerwithEVENTSComplete.py`

This script computes:

- Power spectral density
- Spectral entropy
- Channel‑pair coherence
- Structural term C
- Entropy term H\_norm
- **Canonical Quant‑Trika coherence KQ = C(1 − H\_norm)**
- Dynamic features (dKQ/dt, KQ variance, KQ z‑score)

It is the ground‑truth implementation used to generate the dataset.

---

# 3. Scientific Value of the Repository

This repository demonstrates how Quant‑Trika can be applied to **real, noisy human EEG** to extract meaningful coherence signatures across cognitive and pharmacological states.

It establishes:

### ✔ A reproducible method for computing canonical KQ on electrophysiology

### ✔ A quantitative bridge between structure (C) and entropy (H\_norm) in the brain

### ✔ Empirical evidence of coherence suppression under sedation

### ✔ Recovery dynamics consistent with Quant‑Trika predictions

### ✔ A clear compliance trail: ethical provenance → computation → interpretation

The result is one of the first fully‑transparent, data‑driven demonstrations of Quant‑Trika applied to real biological signals.

---

# 4. How to Use This Repository

### **1. Run the EEG Engine**

Modify or execute `QKEEGAnalizerwithEVENTSComplete.py` to recompute metrics.

### **2. Load the ZIP Archive**

Use pandas or numpy to inspect per‑window metrics.

### **3. Read the Reports**

They explain every step of:

- preprocessing
- computation
- aggregation
- interpretation

### **4. Extend the Analysis**

Possible extensions include:

- subject‑level comparisons
- graph‑based coherence networks
- canonical QT invariants beyond KQ
- time‑frequency evolution of structure and entropy

---

# 5. Acknowledgments

The EEG dataset comes from **OpenNeuroDatasets** and follows strict ethical guidelines for de‑identified human research data.

Spanda Foundation © 2025 Artem Brezgin.

---

# 6. License

- The dataset follows OpenNeuro licensing rules.
- The analysis code is free to use for research and educational purposes.
- Quant‑Trika theoretical constructs are © Artem Brezgin, Spanda Foundation.
- artem@quant-trika.org



