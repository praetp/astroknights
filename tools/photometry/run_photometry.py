#!/usr/bin/env python3
"""
Variable star photometry pipeline.

Calibrates light frames, groups by observation session (night) and exposure
time, then registers each group. No stacking — output is ready for manual
photometry in siril GUI.

Must be run from the directory containing Lights/, Flats/, etc.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

try:
    from astropy.io import fits
except ImportError:
    print("ERROR: astropy is required. Install with: pip install astropy")
    sys.exit(1)

# Session gap threshold: frames more than this apart start a new session
SESSION_GAP = timedelta(hours=8)

FIT_SUFFIXES = (".fit", ".fits", ".fit.fz")


def apply_low_priority():
    os.nice(19)
    subprocess.run(["ionice", "-c", "3", "-p", str(os.getpid())], check=True)


def run_siril(script: str):
    subprocess.run(["siril", "-s", "-"], input=script, text=True, check=True)


def find_light_frames(search_dir: Path) -> list[Path]:
    frames = []
    for p in search_dir.rglob("*"):
        if p.is_file() and p.name.lower().endswith(FIT_SUFFIXES):
            frames.append(p)
    return frames


def read_header(path: Path) -> tuple[datetime, float]:
    with fits.open(path) as hdul:
        header = hdul[0].header
        date_obs = header["DATE-OBS"]
        exptime = float(header["EXPTIME"])
    dt = datetime.fromisoformat(date_obs.replace("Z", "+00:00"))
    # Strip timezone for comparison (treat all as UTC)
    dt = dt.replace(tzinfo=None)
    return dt, exptime


def read_manifest(seq_dir: Path) -> set[str] | None:
    m = seq_dir / ".frames_manifest"
    if not m.exists():
        return None
    return set(m.read_text().splitlines())


def write_manifest(seq_dir: Path, frames: list[Path]):
    m = seq_dir / ".frames_manifest"
    m.write_text("\n".join(sorted(f.name for f in frames)))


def sequence_is_current(seq_dir: Path, frames: list[Path]) -> bool:
    existing = read_manifest(seq_dir)
    if existing is None:
        return False
    return existing == {f.name for f in frames}


def wipe_sequence(seq_dir: Path):
    shutil.rmtree(seq_dir / "lights", ignore_errors=True)
    shutil.rmtree(seq_dir / "process", ignore_errors=True)
    (seq_dir / ".frames_manifest").unlink(missing_ok=True)


def group_frames(frames: list[Path]) -> dict[tuple[str, float], list[Path]]:
    """Group frames by (session_date, exptime)."""
    # Read headers
    metadata = []
    for f in frames:
        try:
            dt, exptime = read_header(f)
            metadata.append((dt, exptime, f))
        except Exception as e:
            print(f"WARNING: Could not read header from {f}: {e}")

    if not metadata:
        return {}

    # Sort by date
    metadata.sort(key=lambda x: x[0])

    # Split into sessions by gap
    sessions: list[list[tuple[datetime, float, Path]]] = [[metadata[0]]]
    for i in range(1, len(metadata)):
        gap = metadata[i][0] - metadata[i - 1][0]
        if gap > SESSION_GAP:
            sessions.append([])
        sessions[-1].append(metadata[i])

    # Group by (session_date, exptime) — date from first frame in session
    groups: dict[tuple[str, float], list[Path]] = {}
    for session in sessions:
        sess_date = session[0][0].strftime("%Y%m%d")
        for dt, exptime, path in session:
            key = (sess_date, exptime)
            groups.setdefault(key, []).append(path)

    return groups


def make_masters(cwd: Path) -> tuple[str, str, str]:
    """Build calibration masters and return siril args for each."""
    masters_dir = cwd / "masters"
    masters_dir.mkdir(exist_ok=True)

    # --- Bias ---
    bias_arg = ""
    bias_master = masters_dir / "masterBias.fit.fz"
    bias_master_plain = masters_dir / "masterBias.fit"
    biases_dir = None

    if (cwd / "Bias").is_dir() and any((cwd / "Bias").iterdir()):
        biases_dir = cwd / "Bias"
    elif (cwd / "biases").exists():
        biases_dir = cwd / "biases"

    if bias_master.exists() or bias_master_plain.exists():
        print("Reusing masterBias")
        bias_arg = f"-bias={masters_dir}/masterBias"
    elif biases_dir:
        process_dir = cwd / "process"
        process_dir.mkdir(exist_ok=True)
        run_siril(f"""requires 1.3.4
cd {cwd}
cd biases
convert bias -out=../process
cd ../process
stack bias rej 3 3 -nonorm -out=../masters/masterBias
cd ..
""")
        bias_arg = f"-bias={masters_dir}/masterBias"
        print("Created masterBias")
    else:
        # Synthetic bias for ZWO 533
        bias_arg = '-bias="=40*$OFFSET"'
        print("No bias frames — using synthetic bias")

    # --- Flat ---
    flat_arg = ""
    flat_master = masters_dir / "masterFlat.fit.fz"
    flat_master_plain = masters_dir / "masterFlat.fit"
    flats_dir = None

    if (cwd / "Flat").is_dir() and any((cwd / "Flat").iterdir()):
        flats_dir = cwd / "Flat"
    elif (cwd / "flats").exists():
        flats_dir = cwd / "flats"

    if flat_master.exists() or flat_master_plain.exists():
        print("Reusing masterFlat")
        flat_arg = f"-flat={masters_dir}/masterFlat"
    elif flats_dir:
        process_dir = cwd / "process"
        process_dir.mkdir(exist_ok=True)
        run_siril(f"""requires 1.3.4
cd {cwd}
cd flats
convert flat -out=../process
cd ../process
calibrate flat {bias_arg}
stack pp_flat rej 3 3 -norm=mul -out=../masters/masterFlat
cd ..
""")
        flat_arg = f"-flat={masters_dir}/masterFlat"
        print("Created masterFlat")
        shutil.rmtree(cwd / "process", ignore_errors=True)
    else:
        print("WARNING: No flats — you may have vignetting in results")

    # --- Dark ---
    dark_arg = ""
    dark_master = masters_dir / "masterDark.fit.fz"
    dark_master_plain = masters_dir / "masterDark.fit"
    darks_dir = None

    if (cwd / "Dark").is_dir() and any((cwd / "Dark").iterdir()):
        darks_dir = cwd / "Dark"
    elif (cwd / "darks").exists():
        darks_dir = cwd / "darks"

    if dark_master.exists() or dark_master_plain.exists():
        print("Reusing masterDark")
        dark_arg = f"-dark={masters_dir}/masterDark -cc=dark"
    elif darks_dir:
        process_dir = cwd / "process"
        process_dir.mkdir(exist_ok=True)
        run_siril(f"""requires 1.3.4
cd {cwd}
cd darks
convert dark -out=../process
cd ../process
stack dark rej 3 3 -nonorm -out=../masters/masterDark
cd ..
""")
        dark_arg = f"-dark={masters_dir}/masterDark -cc=dark"
        print("Created masterDark")
        shutil.rmtree(cwd / "process", ignore_errors=True)
    else:
        print("WARNING: No darks — expect elevated noise and hot pixels")

    return bias_arg, dark_arg, flat_arg


def process_sequence(
    seq_dir: Path,
    frames: list[Path],
    bias_arg: str,
    dark_arg: str,
    flat_arg: str,
    cwd: Path,
):
    """Convert, calibrate, and register one (session, exptime) sequence."""
    process_dir = seq_dir / "process"
    process_dir.mkdir(parents=True, exist_ok=True)

    # Write a file listing frame paths for siril's convert command
    # siril convert works on a directory, so symlink all frames into seq_dir
    lights_link_dir = seq_dir / "lights"
    lights_link_dir.mkdir(exist_ok=True)
    for f in frames:
        link = lights_link_dir / f.name
        if not link.exists():
            link.symlink_to(f.resolve())

    calibrate_args = f"{bias_arg} {dark_arg} {flat_arg} -cfa -equalize_cfa -debayer".strip()

    run_siril(f"""requires 1.3.4
cd {seq_dir}
cd lights
convert light -out=../process
cd ../process
calibrate light {calibrate_args}
register pp_light -2pass
cd ..
""")


def main():
    parser = argparse.ArgumentParser(
        description="Variable star photometry pipeline.",
        epilog=(
            "Run from the directory containing Lights/, Flats/, Darks/, etc.\n"
            "\n"
            "Examples:\n"
            "  cd /data/targets/V404Cyg && python3 run_photometry.py\n"
            "  python3 run_photometry.py --recompute\n"
            "\n"
            "Output: registered frames in session_YYYYMMDD_EXPs/process/r_pp_light_*.fit\n"
            "Load a sequence file (.seq) in the siril GUI to run photometry."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--recompute",
        action="store_true",
        help=(
            "Force reprocessing of all sequences even if they are up to date. "
            "Masters in masters/ are never touched."
        ),
    )
    args = parser.parse_args()

    apply_low_priority()

    cwd = Path.cwd()

    # Remove empty files
    for p in cwd.rglob("*"):
        if p.is_file() and p.stat().st_size == 0:
            print(f"Removing empty file: {p}")
            p.unlink()

    # Build calibration masters
    print("\n=== Building calibration masters ===")
    bias_arg, dark_arg, flat_arg = make_masters(cwd)

    # Find and group light frames
    print("\n=== Scanning light frames ===")
    lights_search = cwd
    # Support Lights/ or lights/ subdirectory, or frames in cwd directly
    for candidate in ("Lights", "lights", "Light", "light"):
        d = cwd / candidate
        if d.is_dir():
            lights_search = d
            break

    frames = find_light_frames(lights_search)
    if not frames:
        print("ERROR: No FITS light frames found.")
        sys.exit(1)
    print(f"Found {len(frames)} light frames")

    groups = group_frames(frames)
    if not groups:
        print("ERROR: Could not group any frames (header read failures?).")
        sys.exit(1)

    sessions_set = {k[0] for k in groups}
    print(f"Detected {len(sessions_set)} session(s), {len(groups)} sequence(s):")
    for (sess_date, exptime), grp_frames in sorted(groups.items()):
        print(f"  session_{sess_date}_{exptime:.0f}s  — {len(grp_frames)} frame(s)")

    if args.recompute:
        print("\n--recompute: wiping all sequence dirs before processing")
        for (sess_date, exptime) in groups:
            seq_name = f"session_{sess_date}_{exptime:.0f}s"
            seq_dir = cwd / seq_name
            if seq_dir.exists():
                wipe_sequence(seq_dir)

    # Process each sequence
    print("\n=== Processing sequences ===")
    for (sess_date, exptime), grp_frames in sorted(groups.items()):
        seq_name = f"session_{sess_date}_{exptime:.0f}s"
        seq_dir = cwd / seq_name

        if not args.recompute and sequence_is_current(seq_dir, grp_frames):
            print(f"  {seq_name}: up to date, skipping")
            continue

        wipe_sequence(seq_dir)
        print(f"\n--- {seq_name} ({len(grp_frames)} frames) ---")
        process_sequence(seq_dir, grp_frames, bias_arg, dark_arg, flat_arg, cwd)
        write_manifest(seq_dir, grp_frames)
        print(f"Done: {seq_dir / 'process'}")

    print("\n=== Photometry pipeline complete ===")
    print("Registered frames: session_YYYYMMDD_EXPs/process/r_pp_light_*.fit")
    print("Load a sequence in siril GUI for photometry.")


if __name__ == "__main__":
    main()
