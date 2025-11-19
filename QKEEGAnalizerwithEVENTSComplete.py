# =============================================================================
# KQ Anesthesia EEG Engine — HYBRID VERSION
#
# This version combines:
# 1. The "naive" (original, simple) calculations for KQ, C, and H_norm
#    as requested by the user from the "old" code.
# 2. The "advanced" architecture from the new code:
#    - GUI for folder/subject selection.
#    - No automatic download.
#    - Saves all metrics from the Technical Specification (TS) to CSV.
#    - Plots all 3 metrics (KQ, C, H) on separate subplots.
#    - Fixes channel mismatches.
#    - All comments are in English.
# =============================================================================

import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch, coherence, butter, lfilter
import mne
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox
import warnings

# Suppress common warnings, e.g., from MNE
warnings.filterwarnings("ignore")

# ------------------------------- CONFIG ---------------------------------------
# The default subject ID. This can be changed in the GUI.
# Set to 1022 as per user's "old" code example.
DEFAULT_SUBJECT_ID = "1022"
# -----------------------------------------------------------------------------

# =============================================================================
# 1. (REMOVED) Download dataset
#    Data is now loaded from a user-selected local folder.
# =============================================================================

# =============================================================================
# 2. Load full cycle + events
# =============================================================================
def load_full_cycle_and_events(dataset_path, subject_id):
    """
    Loads and concatenates all EEG files for a single subject from a BIDS-like directory.
    Also loads and synchronizes event data from .tsv files.

    Args:
        dataset_path (str): The path to the root of the dataset (e.g., '.../ds005620').
        subject_id (str): The subject identifier (e.g., '1022').

    Returns:
        tuple: (data, sfreq, phase_labels, duration, events_df)
    """
    
    # Define the path to the subject's EEG data
    eeg_path = os.path.join(dataset_path, f"sub-{subject_id}", "eeg")
    
    # Define the expected files and their order of concatenation
    order = [
        ("awake_EC", f"sub-{subject_id}_task-awake_acq-EC_eeg.vhdr"),
        ("awake_EO", f"sub-{subject_id}_task-awake_acq-EO_eeg.vhdr"),
        ("sed_run1", f"sub-{subject_id}_task-sed_acq-rest_run-1_eeg.vhdr"),
        ("sed_run2", f"sub-{subject_id}_task-sed_acq-rest_run-2_eeg.vhdr"),
        ("sed_run3", f"sub-{subject_id}_task-sed_acq-rest_run-3_eeg.vhdr"),
        ("pre_run1", f"sub-{subject_id}_task-sed2_acq-rest_run-1_eeg.vhdr"),
        ("pre_run2", f"sub-{subject_id}_task-sed2_acq-rest_run-2_eeg.vhdr"),
        ("pre_run3", f"sub-{subject_id}_task-sed2_acq-rest_run-3_eeg.vhdr"),
    ]
    
    raw_list = []       # To store MNE Raw objects for concatenation
    phase_labels = []   # To store (start, end, name) for plotting
    current_t = 0.0     # Global time tracker
    
    # --- Load all event files ---
    events_all = []
    for task in ["sed", "sed2"]:
        for run in [1, 2, 3]:
            tsv_path = os.path.join(eeg_path, f"sub-{subject_id}_task-{task}_acq-rest_run-{run}_events.tsv")
            if os.path.exists(tsv_path):
                try:
                    df = pd.read_csv(tsv_path, sep='\t')
                    df['task'] = task
                    df['run'] = run
                    events_all.append(df)
                except Exception as e:
                    print(f"Warning: Could not read events file {tsv_path}: {e}")
            
    events_df = pd.concat(events_all, ignore_index=True) if events_all else pd.DataFrame()

    # --- Load and concatenate EEG files ---
    print("Loading and concatenating EEG files...")
    for phase_name, fname in tqdm(order, desc="Loading phases"):
        path = os.path.join(eeg_path, fname)
        if not os.path.exists(path):
            print(f"Warning: File not found, skipping: {fname}")
            continue
        try:
            raw = mne.io.read_raw_brainvision(path, preload=True, verbose=False)
            raw.resample(500.0, npad="auto")
            raw.pick_types(eeg=True, exclude='bads')
            duration = raw.times[-1]
            raw_list.append(raw)
            phase_labels.append((current_t, current_t + duration, phase_name))
            current_t += duration
        except Exception as e:
            print(f"Error loading {fname}: {e}")
            
    if not raw_list:
        raise FileNotFoundError(f"No EEG data loaded for subject {subject_id}. Check path: {eeg_path}")

    # --- FIX for mismatched channels (from new code) ---
    try:
        common_channels = set(raw_list[0].ch_names)
        for r in raw_list[1:]:
            common_channels.intersection_update(r.ch_names)
        
        common_channels_list = sorted(list(common_channels)) 
        
        # --- ROBUSTNESS CHECK (NEW) ---
        # Check if we have at least 2 channels left to calculate coherence
        if len(common_channels_list) < 2:
            raise ValueError(f"Analysis failed: Coherence calculation requires at least 2 common EEG channels across all files.\n"
                             f"This subject ({subject_id}) only has {len(common_channels_list)} common channel(s): {common_channels_list}")
        # --- END OF CHECK ---

        print(f"Found {len(common_channels_list)} common channels. Forcing all files to match...")
        
        for raw in raw_list:
            raw.pick_channels(common_channels_list)
    except Exception as e:
        print(f"Error during channel intersection: {e}")
        raise e
    # --- End of fix ---

    full_raw = mne.concatenate_raws(raw_list)
    data = full_raw.get_data()
    sfreq = full_raw.info['sfreq']
    
    # --- Preprocessing: Band-pass filter ---
    print("Applying band-pass filter (0.5 - 45 Hz)...")
    nyq = 0.5 * sfreq
    b, a = butter(5, [0.5/nyq, 45.0/nyq], btype='band')
    data = lfilter(b, a, data, axis=1)
    
    # --- Correct event times ---
    if not events_df.empty and 'onset' in events_df.columns:
        print("Synchronizing event times...")
        run_starts = {name: s for s, e, name in phase_labels}
        def get_global_onset(row):
            phase_name = f"{row['task']}_run{row['run']}"
            if row['task'] == "sed2":
                phase_name = f"pre_run{row['run']}"
            start_time = run_starts.get(phase_name, 0)
            return start_time + row['onset']
        events_df['onset_global'] = events_df.apply(get_global_onset, axis=1)
    
    print(f"Total duration loaded: {full_raw.times[-1]:.2f} seconds")
    return data, sfreq, phase_labels, full_raw.times[-1], events_df

# =============================================================================
# 3. KQ + Event Analyzer
# =============================================================================
def analyze_with_events(data, sfreq, phase_labels, events_df, subject_id, win_sec, overlap_perc):
    """
    Calculates KQ, C, H_norm using the SIMPLE/ORIGINAL logic.
    Collects all other TS metrics.
    Plots all 3 metrics on separate subplots.
    """
    
    # --- Analysis parameters ---
    overlap = overlap_perc
    win_samples = int(win_sec * sfreq)
    step = int(win_samples * (1 - overlap/100))

    # Define standard EEG bands (for TS metrics)
    BANDS = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 12),
        'beta': (12, 30),
        'gamma': (30, 45)
    }
    
    results = []        # To store results for each window
    times, kqs, cs, hs = [], [], [], [] # For plotting
    
    # --- Setup live plot (from new code) ---
    plt.ion() 
    fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    fig.suptitle(f"KQ, C, H_norm + Events — sub-{subject_id}", fontsize=16)
    
    # --- Sliding window analysis ---
    for start in tqdm(range(0, data.shape[1] - win_samples + 1, step), desc="Calculating KQ"):
        
        # Get data for the current window
        win = data[:, start:start+win_samples]
        
        # --- Calculate time ---
        t_start_sec = start / sfreq
        t_end_sec = (start + win_samples) / sfreq
        t_mid = (start + win_samples//2) / sfreq
        
        # --- 0. Calculate ALL TS metrics (from new code) ---
        # These are for the CSV file
        gfp = np.std(win, axis=0).mean()
        mean_amp = np.mean(win)
        variance = np.var(win)
        
        f, psd = welch(win, fs=sfreq, nperseg=win_samples, axis=1)
        psd_avg_ts = np.nanmean(psd, axis=0) # Use nanmean for robust TS metrics
        psd_avg_ts = np.nan_to_num(psd_avg_ts)
        total_power = np.sum(psd_avg_ts)
        if total_power <= 0: total_power = 1e-12
        
        band_powers = {}
        for band, (f_low, f_high) in BANDS.items():
            band_mask = (f >= f_low) & (f < f_high)
            power_in_band = np.sum(psd_avg_ts[band_mask])
            band_powers[f'band_power_{band}'] = power_in_band
            band_powers[f'relative_power_{band}'] = power_in_band / total_power

        # --- START: "Old" Code Calculation Block ---
        # These 3 metrics (KQ, C, H) are calculated EXACTLY as per
        # the user-provided "old" script for the live plot.
        
        # 1. H_norm (Naive)
        try:
            # We must use psd (not psd_avg_ts) to match old code
            f_naive, psd_naive = welch(win, fs=sfreq, nperseg=win_samples, axis=1)
            psd_avg_naive = psd_naive.mean(axis=0) 
            psd_avg_naive /= (psd_avg_naive.sum() + 1e-12)
            H_norm = -np.sum(psd_avg_naive * np.log2(psd_avg_naive + 1e-12)) / np.log2(len(psd_avg_naive))
        except Exception:
            H_norm = np.nan # Set to NaN on failure

        # 2. Coherence (Naive)
        n = min(20, win.shape[0])
        C = 0.0
        pairs = 0
        try:
            for i in range(n):
                for j in range(i+1, n):
                    # --- CRITICAL FIX: Use NO nperseg ---
                    # This matches the old code's logic (which defaults to nperseg=256)
                    _, coh = coherence(win[i], win[j], fs=sfreq)
                    # --- END FIX ---
                    C += coh.mean() 
                    pairs += 1
            C = C / pairs if pairs > 0 else 0.0
        except Exception:
            C = np.nan # Set to NaN on failure
        
        # 3. KQ (Naive)
        KQ = C * (1 - H_norm)
        
        # --- END: "Old" Code Calculation Block ---

        # --- Stabilization for plotting ---
        # Prevent plotting from crashing if old calcs produce NaN
        KQ_plot = np.nan_to_num(KQ, nan=0.0, posinf=0.0, neginf=0.0)
        C_plot = np.nan_to_num(C, nan=0.0, posinf=0.0, neginf=0.0)
        H_plot = np.nan_to_num(H_norm, nan=0.0, posinf=0.0, neginf=0.0)

        # Store all metrics for this window
        metrics_dict = {
            "t_start_sec": t_start_sec,
            "t_end_sec": t_end_sec,
            "t_mid_sec": t_mid,
            "KQ_naive": KQ, # Store the "pure" value in CSV
            "C_naive": C,
            "H_norm_naive": H_norm,
            "gfp": gfp,
            "mean_amplitude": mean_amp,
            "variance": variance,
        }
        # Add all band powers to the dictionary
        metrics_dict.update(band_powers)
        
        results.append(metrics_dict)
        # Append stabilized values to plot lists
        times.append(t_mid)
        kqs.append(KQ_plot)
        cs.append(C_plot)
        hs.append(H_plot)
        
        # --- Update live plot (every 10 iterations) ---
        if len(results) % 10 == 0 or start + step >= data.shape[1] - win_samples:
            for ax in axes: ax.cla() # Clear all axes

            # Plot KQ
            axes[0].plot(times, kqs, 'b-', lw=2, label="KQ")
            axes[0].set_ylabel("KQ")
            axes[0].legend(loc='upper left')
            axes[0].grid(True)

            # Plot C
            axes[1].plot(times, cs, 'g-', lw=1, label="C (Coherence)", alpha=0.7)
            axes[1].set_ylabel("C (Coherence)")
            axes[1].legend(loc='upper left')
            axes[1].grid(True)

            # Plot H_norm
            axes[2].plot(times, hs, 'r-', lw=1, label="H_norm (Entropy)", alpha=0.7)
            axes[2].set_ylabel("H_norm (Entropy)")
            axes[2].set_xlabel("Time (s)")
            axes[2].legend(loc='upper left')
            axes[2].grid(True)
            
            # Apply phase shading and events to all subplots
            for ax in axes:
                # Set sane Y-limits in case of outliers
                if times: # check if list is not empty
                    if ax == axes[0]: ax.set_ylim(min(kqs)-0.1, max(kqs)+0.1)
                if ax == axes[1]: ax.set_ylim(-0.1, 1.1) # Coherence is 0-1
                if ax == axes[2]: ax.set_ylim(-0.1, 1.1) # H_norm is 0-1
                
                ylim = ax.get_ylim()

                for t0, t1, name in phase_labels:
                    ax.axvspan(t0, t1, alpha=0.1, color='gray')
                    ax.text(t0 + 5, ylim[1] * 0.9, name, rotation=90, fontsize=9)
                
                if not events_df.empty and 'onset_global' in events_df.columns:
                    for _, ev in events_df.iterrows():
                        t = ev['onset_global']
                        label = ev.get('trial_type', '') or ev.get('value', '')
                        color = 'red' if 'awakening' in str(label).lower() else \
                                'green' if 'induction' in str(label).lower() else \
                                'purple' if 'dream' in str(label).lower() else 'orange'
                        ax.axvline(t, color=color, linestyle='--', alpha=0.7)
                        
                        if ax == axes[0] and 'dream' in str(label).lower():
                            ax.text(t, ylim[1]*0.8, "DREAM", color='purple', fontsize=10, ha='center')
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig.canvas.draw()
            plt.pause(0.01)
            
    plt.ioff() # Turn off interactive mode
    print("Analysis complete.")
    return results, events_df

# =============================================================================
# GUI + Full Analyzer (from new code)
# =============================================================================
class KQApp:
    """
    Main application class for the GUI.
    Handles folder selection, analysis execution, and saving results.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("KQ + Dream Report Analyzer (Hybrid)")
        self.root.geometry("800x400")
        
        self.dataset_path = None

        # --- Title ---
        tk.Label(root, text="KQ Engine + Event Analyzer (Hybrid)", font=("Arial", 16, "bold"), fg="navy").pack(pady=10)
        
        # --- Subject ID Input ---
        subj_frame = tk.Frame(root)
        subj_frame.pack(pady=5)
        tk.Label(subj_frame, text="Subject ID:", font=("Arial", 12)).pack(side="left", padx=5)
        self.subject_id_var = tk.StringVar(value=DEFAULT_SUBJECT_ID)
        tk.Entry(subj_frame, textvariable=self.subject_id_var, width=10, font=("Arial", 12)).pack(side="left")
        
        # --- Data Folder Selection ---
        self.folder_label_var = tk.StringVar(value="No data folder selected.")
        self.folder_label = tk.Label(root, textvariable=self.folder_label_var, fg="blue", wraplength=750)
        self.folder_label.pack(pady=10)
        
        tk.Button(root, text="1. Select Data Folder", command=self.select_data_folder, bg="orange", width=30, height=2).pack(pady=5)
        
        # --- Start Button ---
        tk.Button(root, text="2. Start Full Analysis + Events", command=self.start_analysis, bg="green", fg="white", width=30, height=2).pack(pady=10)
        
        # --- Status Label ---
        self.status_var = tk.StringVar(value="Ready. Please select a data folder.")
        tk.Label(root, textvariable=self.status_var, fg="darkblue", wraplength=750, font=("Arial", 10)).pack(pady=20, side="bottom")

    def select_data_folder(self):
        """
        Opens a dialog to select the root data directory.
        """
        try:
            path = filedialog.askdirectory(title="Select the root data folder (e.g., .../ds005620)")
            if path:
                subject_id = self.subject_id_var.get()
                expected_sub_folder = os.path.join(path, f"sub-{subject_id}")
                if not os.path.isdir(expected_sub_folder):
                    self.status_var.set(f"Warning: Folder selected, but sub-{subject_id} folder not found inside.")
                else:
                    self.status_var.set(f"Data folder selected. Ready to analyze sub-{subject_id}.")
                
                self.dataset_path = path
                self.folder_label_var.set(f"Selected Folder: {self.dataset_path}")
                self.root.update()
        except Exception as e:
            messagebox.showerror("Error", f"Could not select folder: {e}")

    def start_analysis(self):
        """
        Runs the full analysis pipeline: load, process, analyze, and save.
        """
        if not self.dataset_path:
            messagebox.showerror("Error", "Please select a data folder first!")
            return
            
        subject_id = self.subject_id_var.get()
        if not subject_id:
            messagebox.showerror("Error", "Please enter a Subject ID!")
            return

        self.status_var.set(f"Starting analysis for sub-{subject_id}...")
        self.root.update()
        
        try:
            # --- 0. Define analysis parameters ---
            win_sec = 2.0
            overlap_perc = 50

            # --- 2. Load and process data ---
            self.status_var.set(f"Loading data for sub-{subject_id} from {self.dataset_path}...")
            self.root.update()
            data, sfreq, phases, duration, events = load_full_cycle_and_events(self.dataset_path, subject_id)
            
            # --- 3. Run KQ analysis ---
            self.status_var.set("Data loaded. Calculating KQ (using naive method) and events...")
            self.root.update()
            results, events = analyze_with_events(data, sfreq, phases, events, subject_id, win_sec, overlap_perc)
            
            # --- 4. Create output directory ---
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = os.path.join(self.dataset_path, f"resultatKQEEG{timestamp}")
            os.makedirs(os.path.join(out_dir, "plots"), exist_ok=True)
            self.status_var.set(f"Analysis complete. Saving results to: {out_dir}")
            self.root.update()
            
            # --- 5. Save results ---
            df = pd.DataFrame(results)

            # --- Add derived metrics (as per TS) ---
            if not df.empty:
                # Calculate time difference
                dt = df['t_mid_sec'].diff().mean()
                if dt is None or np.isnan(dt) or dt == 0:
                    dt = win_sec * (1 - overlap_perc / 100.0)

                # 1. dKQ/dt (based on the naive KQ)
                df['dKQ_dt'] = df['KQ_naive'].diff() / dt
                df['dKQ_dt'].fillna(0, inplace=True)
                
                # 2. KQ Local Variance
                df['KQ_local_variance'] = df['KQ_naive'].rolling(window=5, min_periods=1, center=True).var()
                df['KQ_local_variance'].fillna(0, inplace=True)
                
                # 3. Z-score KQ (relative to first 'awake' phase)
                baseline_phase = None
                for s, e, name in phases:
                    if 'awake' in name:
                        baseline_phase = (s, e)
                        break
                
                baseline_mean = 0.0; baseline_std = 1.0
                if baseline_phase:
                    s, e = baseline_phase
                    baseline_df = df[(df['t_mid_sec'] >= s) & (df['t_mid_sec'] <= e)]
                    if not baseline_df.empty:
                        baseline_mean = baseline_df['KQ_naive'].mean()
                        baseline_std = baseline_df['KQ_naive'].std()
                        if baseline_std < 1e-6 or np.isnan(baseline_std): baseline_std = 1.0
                
                df['KQ_zscore'] = (df['KQ_naive'] - baseline_mean) / (baseline_std + 1e-12)

            # Save KQ time-series data (as per TS)
            df.to_csv(os.path.join(out_dir, "kq_timeseries_hybrid.csv"), index=False)
            
            if not events.empty:
                events.to_csv(os.path.join(out_dir, "events_full_synchronized.tsv"), sep='\t', index=False)
            
            # --- 6. Save Metadata (as per TS) ---
            metadata = {
                "run_id": f"sub-{subject_id}_{timestamp}",
                "subject_id": subject_id,
                "dataset_name": os.path.basename(self.dataset_path),
                "analysis_timestamp": timestamp,
                "calculation_mode": "Hybrid (Naive KQ/C/H, Full TS Metrics)",
                "sampling_rate_hz_after_resample": sfreq,
                "window_length_sec": win_sec,
                "window_overlap_perc": overlap_perc,
                "filter_band_hz": [0.5, 45.0],
                "phases_loaded": phases,
            }
            meta_filename = os.path.join(out_dir, "run_metadata.json")
            try:
                with open(meta_filename, 'w') as f:
                    json.dump(metadata, f, indent=4)
            except Exception as e:
                print(f"Warning: Could not save metadata JSON: {e}")

            # --- 7. Save final summary plot ---
            print("Saving final plot...")
            fig, axes = plt.subplots(3, 1, figsize=(20, 15), sharex=True)
            fig.suptitle(f"KQ, C, H_norm (Naive Calc) + Events — sub-{subject_id}", fontsize=16)
            
            # --- START FIX ---
            # The variables 'times', 'kqs', 'cs', 'hs' do not exist here.
            # We must use the 'df' DataFrame which has the data.
            
            # Create plot-safe columns in the DataFrame, just like we did for the live plot
            df['KQ_plot'] = np.nan_to_num(df['KQ_naive'], nan=0.0, posinf=0.0, neginf=0.0)
            df['C_plot'] = np.nan_to_num(df['C_naive'], nan=0.0, posinf=0.0, neginf=0.0)
            df['H_plot'] = np.nan_to_num(df['H_norm_naive'], nan=0.0, posinf=0.0, neginf=0.0)
            
            # Plot from the DataFrame columns
            axes[0].plot(df['t_mid_sec'], df['KQ_plot'], 'b-', lw=2, label="KQ")
            axes[0].set_ylabel("KQ", fontsize=12)
            axes[0].legend(loc='upper left'); axes[0].grid(True)
            
            axes[1].plot(df['t_mid_sec'], df['C_plot'], 'g-', lw=1.5, label="C (Coherence)", alpha=0.8)
            axes[1].set_ylabel("C (Coherence)", fontsize=12)
            axes[1].legend(loc='upper left'); axes[1].grid(True)

            axes[2].plot(df['t_mid_sec'], df['H_plot'], 'r-', lw=1.5, label="H_norm (Entropy)", alpha=0.8)
            axes[2].set_ylabel("H_norm (Entropy)", fontsize=12)
            axes[2].set_xlabel("Time (s)", fontsize=12)
            axes[2].legend(loc='upper left'); axes[2].grid(True)
            # --- END FIX ---

            for ax in axes:
                # Set sane Y-limits in case of outliers
                if not df.empty:
                    # Fix ylim to use the correct DataFrame column
                    if ax == axes[0] and not df['KQ_plot'].empty: 
                        ax.set_ylim(min(df['KQ_plot'])-0.1, max(df['KQ_plot'])+0.1)
                ax.set_ylim(bottom=-0.1) # Ensure 0 is visible
                if ax == axes[1]: ax.set_ylim(-0.1, 1.1) # Coherence is 0-1
                if ax == axes[2]: ax.set_ylim(-0.1, 1.1) # H_norm is 0-1
                
                ylim = ax.get_ylim()
                for t0,t1,name in phases:
                    ax.axvspan(t0, t1, alpha=0.1, color='gray')
                    ax.text(t0 + 5, ylim[1] * 0.95, name, rotation=90, fontsize=10)
                    
                if not events.empty and 'onset_global' in events.columns:
                    for _, ev in events.iterrows():
                        t = ev['onset_global']
                        label = str(ev.get('trial_type', '') or ev.get('value', ''))
                        color = 'red' if 'awakening' in label.lower() else \
                                'purple' if 'dream' in label.lower() else \
                                'green' if 'induction' in str(label).lower() else 'orange'
                        ax.axvline(t, color=color, linestyle='--', alpha=0.7)
                        
                        if ax == axes[0] and 'dream' in label.lower():
                            ax.text(t, ylim[1] * 0.85, "DREAM", color='purple', fontsize=12, ha='center', weight='bold')
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plot_filename = os.path.join(out_dir, "plots", f"KQ_hybrid_with_events_sub-{subject_id}.png")
            plt.savefig(plot_filename, dpi=200)
            plt.close()
            
            messagebox.showinfo("Analysis Complete!", f"Hybrid analysis saved to:\n{out_dir}")
            self.status_var.set(f"Complete! Results saved for sub-{subject_id}.")
            
        except ValueError as ve:
            # Catch the specific error we added for channel mismatch
            messagebox.showerror("ValueError", f"{ve}")
            self.status_var.set("Error: Not enough common channels.")
        except FileNotFoundError as fnf_error:
            messagebox.showerror("File Not Found Error", f"{fnf_error}\n\nPlease check the selected folder and Subject ID.")
            self.status_var.set("Error. Check folder and Subject ID.")
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred:\n{str(e)}")
            self.status_var.set("Error. Analysis failed.")

# =============================================================================
# Main execution
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = KQApp(root)
    root.mainloop()