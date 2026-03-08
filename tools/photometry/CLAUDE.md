# Variable Star Photometry Pipeline

## Purpose
`run_photometry.py` prepares OSC light frames for variable star photometry in Siril.
It is distinct from `../siril/run_siril.sh`, which is for deep-sky stacking.

**No stacking is performed.** Output is registered sequences ready for manual
photometry in the Siril GUI.

## Usage
Run from the directory containing your observation data (Lights/, Flats/, etc.):
```bash
python3 /path/to/run_photometry.py
```

## Dependencies
- `astropy` — FITS header reading (`DATE-OBS`, `EXPTIME`)
- `siril` >= 1.3.4

## Workflow

### 1. Low priority startup
`os.nice(19)` + `ionice -c 3` applied at startup (same pattern as `run_siril.sh`).

### 2. Calibration masters
Masters are built once and shared across all sessions/exposures.
Stored in `masters/` in the working directory.
- **Bias**: reuse `masters/masterBias.fit[.fz]` if present; otherwise build from `biases/` or `Bias/`; fallback: synthetic bias `-bias="=40*$OFFSET"` (tuned for ZWO 533)
- **Flat**: reuse `masters/masterFlat.fit[.fz]` if present; otherwise build from `flats/` or `Flat/` using bias
- **Dark**: reuse `masters/masterDark.fit[.fz]` if present; otherwise build from `darks/` or `Dark/`
- OSC only — no narrowband/dualband support

### 3. Frame grouping
- Scans for `*.fit`, `*.fits`, `*.fit.fz` in `Lights/`, `lights/`, `Light/`, `light/`, or cwd
- Reads `DATE-OBS` (datetime) and `EXPTIME` (float) from each FITS header via astropy
- Sorts by `DATE-OBS`
- **Session splitting rule**: gap > 8 hours between two *consecutive* frames = new session
  - A session may span more than 8 hours total — only the gap between adjacent frames matters
  - Sessions spanning midnight are handled correctly by this rule
- Within each session, further split by `EXPTIME`
- Each `(session_index, exptime)` pair = one sequence

### 4. Per-sequence processing
Output directory structure:
```
session_{N}_{exptime}s/
  lights/    ← symlinks to original frames
  process/   ← converted, calibrated, and registered frames
```
Siril steps per sequence:
1. `convert light` → `process/`
2. `calibrate light` with masterBias/masterDark/masterFlat, `-cfa -equalize_cfa -debayer` (OSC)
3. `register pp_light -2pass`

### 5. Output
Registered frames: `session_{N}_{exptime}s/process/r_pp_light_*.fit`
Load a sequence in the Siril GUI for photometry.

## Siril invocation approach
Uses `subprocess.run(['siril', '-s', '-'], input=script, text=True, check=True)` to pipe
Siril's scripting language via stdin. This is the same pattern as `run_siril.sh` and requires
no running Siril instance — appropriate for a standalone CLI pipeline.

**Not used:**
- `sirilpy` — bundled with Siril >= 1.4, requires a running Siril instance to connect to;
  useful for reading data back from Siril (star detections, sequence metadata), not needed here
- `sirilic` — external GUI wizard app, unrelated

## Related files
- `../siril/run_siril.sh` — deep-sky stacking pipeline (reference for master creation logic)
