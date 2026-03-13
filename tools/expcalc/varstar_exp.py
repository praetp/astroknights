#!/usr/bin/env python3
"""
varstar_exp.py — Variable Star Optimal Exposure Calculator

Calculates the optimal exposure time for imaging a variable star, ensuring the
peak pixel does not saturate at the star's maximum (brightest) magnitude.

Usage:
    python3 varstar_exp.py "R Leo" --aperture 200 --focal-length 800
    python3 varstar_exp.py "eta Aql" --aperture 102 --focal-length 714 --gain 200
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Camera database
# ---------------------------------------------------------------------------

CAMERA_DB = {
    "ASI533MC": {
        "name": "ZWO ASI 533 MC Pro",
        "sensor": "IMX533",
        "sensor_type": "osc",       # One-Shot Colour — RGGB Bayer matrix
        "adc_bits": 14,
        "pixel_size_um": 3.76,
        # Calibration points: gain -> (e_per_adu, full_well_e, read_noise_e)
        # Sources:
        #   e_per_adu  : ZWO published gain tables
        #   full_well_e: gain 0   → pixel-well limited (~50 ke⁻, ZWO spec)
        #                gain 100+→ ADC-limited: adc_max × e_per_adu
        #                          (14-bit ADC = 16383 ADU; HCG mode pixel well exceeds this)
        #   read_noise : community SharpCap sensor analysis — verify with your own unit
        "calibration": {
            0:   (3.74, 50000, 3.29),   # pixel-well limited; sat_adu = 50000/3.74 = 13369
            100: (1.00, 16383, 1.68),   # ADC-limited; sat_adu = 16383
            200: (0.50,  8192, 1.54),   # ADC-limited; sat_adu = 8192/0.50 = 16383
        },
    },

    "ASI120MM_Mini": {
        "name": "ZWO ASI 120MM Mini",
        "sensor": "AR0130CS",
        "sensor_type": "mono",      # Monochrome — no Bayer matrix
        "adc_bits": 12,             # 12-bit ADC; max 4095 ADU
        "pixel_size_um": 3.75,
        # Calibration points: gain -> (e_per_adu, full_well_e, read_noise_e)
        # Sources:
        #   full_well_e: 13,000 e⁻ at gain 0 — ZWO product page / retailer specs
        #   e_per_adu  : gain 0 → 13000 / 4095 ≈ 3.17 (pixel-well fills ADC by design)
        #                gain 50+→ ADC-limited: 4095 × e_per_adu (estimated)
        #   read_noise : ~3.5 e⁻ at gain 0 — ZWO product page; higher gains estimated
        #   Verify gains 50 and 100 with SharpCap sensor analysis on your unit.
        "calibration": {
            0:   (3.17, 13000, 3.5),   # pixel-well limited; sat_adu = 13000/3.17 ≈ 4102 → 4095
            50:  (1.00,  4095, 2.0),   # ADC-limited; sat_adu = 4095  (estimated unity gain)
            100: (0.35,  1433, 1.5),   # ADC-limited; sat_adu = 4095  (estimated)
        },
        # Effective QE per filter for the AR0130CS mono sensor.
        # ZWO claims peak QE ~80 %; broadband V-band estimate used here (~70 %).
        # Values = sensor QE × filter in-band transmission for a V-magnitude source.
        # Non-V filters also require a colour correction to the input magnitude — see warning.
        # Verify against a SharpCap sensor analysis or measured flat-field throughput.
        "qe_per_filter": {
            "none":      0.70,
            "uv_ir_cut": 0.66,
            "johnson_v": 0.62,
            "johnson_b": 0.40,   # decent blue response; B-V correction needed
            "johnson_r": 0.65,   # V-R correction needed
            "johnson_i": 0.30,   # reduced NIR response; V-I correction needed
        },
    },
}

# ---------------------------------------------------------------------------
# Filter database
# ---------------------------------------------------------------------------
#
# Each entry stores the effective per-channel QE for the IMX533 (RGGB Bayer)
# through that filter for a solar-like (G2V) star.  Values are
#   integral( QE_channel(λ) × T_filter(λ) × SED(λ) dλ )
# normalised so that the "none" entry matches the bare-sensor broadband QE
# at V-band (~550 nm).  Numbers are approximate; accurate values require a
# full spectral integration against the actual QE and filter curves.
#
# The channel with the highest effective QE saturates first — that is the
# conservative worst-case used for the exposure limit (qe_peak).
# qe_avg is the RGGB-weighted mean: (R + 2G + B) / 4.
#
# photometry_note: shown in output when the VSX V-band magnitude needs a
# colour correction before applying the result to a non-V filter.

FILTER_DB = {
    "none": {
        "name": "No filter (bare sensor)",
        "qe_channels": {"R": 0.50, "G": 0.70, "B": 0.10},
        # Bare IMX533 QE, broadband average centred on V-band (~550 nm).
        # RGGB avg = 0.50.  Green dominant.
        "photometry_note": None,
    },
    "uv_ir_cut": {
        "name": "Optolong UV/IR Cut",
        "qe_channels": {"R": 0.47, "G": 0.68, "B": 0.09},
        # Passes ~400–700 nm, ~95 % peak transmission.
        # Slight reduction in red (IR cut above 700 nm) and blue (UV cut below 400 nm).
        # RGGB avg = 0.48.  Green dominant.
        "photometry_note": None,
    },
    "johnson_v": {
        "name": "Johnson V",
        "qe_channels": {"R": 0.30, "G": 0.62, "B": 0.04},
        # Bandpass 480–690 nm, peak ~550 nm, T_peak ~90 %.
        # Well-matched to green channel; blue and far-red significantly cut.
        # RGGB avg = 0.47.  Green dominant.
        "photometry_note": None,   # V filter matches VSX V magnitudes directly
    },
    "johnson_b": {
        "name": "Johnson B",
        "qe_channels": {"R": 0.02, "G": 0.28, "B": 0.20},
        # Bandpass 360–500 nm, peak ~440 nm, T_peak ~85 %.
        # IMX533 green QE extends to ~400 nm, so green still dominates over blue.
        # Red essentially blocked.  RGGB avg = 0.20.  Green dominant.
        "photometry_note": "VSX magnitude is V-band; a B-V colour correction is needed for accurate photometry.",
    },
    "johnson_r": {
        "name": "Johnson R (Cousins)",
        "qe_channels": {"R": 0.52, "G": 0.25, "B": 0.01},
        # Bandpass 560–740 nm (Cousins R), peak ~650 nm, T_peak ~85 %.
        # Red channel dominant.  RGGB avg = 0.38.
        "photometry_note": "VSX magnitude is V-band; a V-R colour correction is needed for accurate photometry.",
    },
    "johnson_i": {
        "name": "Johnson I (Cousins)",
        "qe_channels": {"R": 0.28, "G": 0.04, "B": 0.00},
        # Bandpass 700–900 nm (Cousins I), peak ~800 nm, T_peak ~85 %.
        # Only red channel effective; very low overall efficiency.  RGGB avg = 0.09.
        "photometry_note": "VSX magnitude is V-band; a V-I colour correction is needed for accurate photometry.",
    },
}

# ---------------------------------------------------------------------------
# Physics constants
# ---------------------------------------------------------------------------

F0_V = 8.94e9       # photons/s/m² for a V=0 (Vega) star (Bessell 1979, V-band zero point)
K_EXT = 0.2         # atmospheric extinction coefficient (mag/airmass, V-band)
T_OPTICS = 0.85     # combined optical throughput
LAMBDA_V = 550e-9   # V-band centre wavelength (m)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

class _HelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, f"\nerror: {message}\n")


def parse_args():
    p = _HelpOnErrorParser(
        description="Calculate optimal exposure time for a variable star.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("star_id",
                   help='Star identifier as used in AAVSO VSX or SIMBAD, e.g. '
                        '"R Leo", "eta Aql", "SS Cyg", "Mira", "chi Cyg", "R Car"')
    p.add_argument("--camera", choices=list(CAMERA_DB.keys()), default="ASI533MC",
                   help="Camera preset (default: ASI533MC)")
    p.add_argument("--gain", type=int, default=100,
                   help="Camera gain (default: 100, unity gain for ASI533MC)")
    p.add_argument("--offset", type=int, default=5,
                   help="Camera offset (default: 5)")
    p.add_argument("--aperture", type=float, default=115.0,
                   help="Telescope aperture in mm (default: 115)")
    p.add_argument("--focal-length", type=float, default=800.0,
                   help="Telescope focal length in mm (default: 800)")
    p.add_argument("--obstruction", type=float, default=0.0,
                   help="Central obstruction ratio 0–1 (default: 0.0)")
    p.add_argument("--seeing", type=float, default=3.0,
                   help="Atmospheric seeing FWHM in arcsec (default: 3.0)")
    p.add_argument("--airmass", type=float, default=1.2,
                   help="Airmass at time of observation (default: 1.2)")
    p.add_argument("--filter", choices=list(FILTER_DB.keys()), default="uv_ir_cut",
                   help="Optical filter (default: uv_ir_cut)")
    p.add_argument("--target-saturation", type=float, default=0.75,
                   help="Target ADU fraction of saturation 0–1 (default: 0.75)")
    p.add_argument("--sky-background", type=float, default=18.0,
                   help="Sky background surface brightness in mag/arcsec² (default: 18.0, Antwerp)")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Star lookup: VSX primary, SIMBAD fallback
# ---------------------------------------------------------------------------

def query_vsx(star_id: str) -> dict | None:
    """Query AAVSO VSX for the star's magnitude range and type."""
    url = "https://www.aavso.org/vsx/index.php"
    params = {"view": "api.object", "format": "json", "ident": star_id}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"[VSX] Request failed: {exc}", file=sys.stderr)
        return None

    try:
        obj = data["VSXObject"]
    except (KeyError, TypeError):
        return None

    # VSX returns an empty list [] when nothing matches, and a dict when found.
    if not isinstance(obj, dict):
        return None

    def _parse_mag(val):
        """Strip limit flags, parentheses, and band letters; return float or None.

        VSX magnitude fields can look like: '9.08 V', '<10.5', '(12.3)', '9.72 V'.
        We strip leading '<>(' and trailing '>)', then take only the first
        whitespace-delimited token so that band designations ('V', 'B', 'R' …)
        are discarded before conversion to float.
        """
        if val is None:
            return None
        s = str(val).strip().lstrip("<>(").rstrip(">)")
        s = s.split()[0] if s else s   # drop trailing band letter, e.g. 'V'
        try:
            return float(s)
        except ValueError:
            return None

    mag_max = _parse_mag(obj.get("MaxMag"))
    mag_min = _parse_mag(obj.get("MinMag"))
    name = obj.get("Name", star_id)
    var_type = obj.get("Type", "?")
    period = obj.get("Period")

    if mag_max is None:
        return None

    return {
        "name": name,
        "type": var_type,
        "mag_max": mag_max,   # brightest (numerically smallest)
        "mag_min": mag_min,
        "period": period,
        "source": "VSX",
    }


def query_simbad(star_id: str) -> dict | None:
    """Fallback: query SIMBAD via astroquery for V-band flux."""
    try:
        from astroquery.simbad import Simbad
    except ImportError:
        print("[SIMBAD] astroquery not installed; skipping fallback.", file=sys.stderr)
        return None

    simbad = Simbad()
    simbad.add_votable_fields("flux(V)", "flux_error(V)", "otype")
    try:
        result = simbad.query_object(star_id)
    except Exception as exc:
        print(f"[SIMBAD] Query failed: {exc}", file=sys.stderr)
        return None

    if result is None or len(result) == 0:
        return None

    row = result[0]

    def _col(name):
        try:
            v = row[name]
            return None if v is None or (hasattr(v, "mask") and v.mask) else float(v)
        except Exception:
            return None

    mag_v = _col("FLUX_V")
    if mag_v is None:
        return None

    otype = str(row.get("OTYPE", "?")).strip()

    # SIMBAD doesn't reliably give us a magnitude *range*; use V as both.
    return {
        "name": star_id,
        "type": otype,
        "mag_max": mag_v,
        "mag_min": None,
        "period": None,
        "source": "SIMBAD (V only — no range available)",
    }


# ---------------------------------------------------------------------------
# Star lookup cache
# ---------------------------------------------------------------------------

CACHE_DIR = Path.home() / ".cache" / "varstar_exp"


def _cache_path(star_id: str) -> Path:
    """Return the cache file path for a given (already-normalised) star ID."""
    safe = re.sub(r"[^\w\-]", "_", star_id).strip("_")
    return CACHE_DIR / f"{safe}.json"


def _load_cache(star_id: str) -> dict | None:
    path = _cache_path(star_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return data["star"]
    except Exception:
        return None


def _save_cache(star_id: str, info: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(star_id)
    payload = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "star": info,
    }
    path.write_text(json.dumps(payload, indent=2))


def _strip_simbad_prefix(star_id: str) -> str:
    """Remove SIMBAD object-type prefixes such as 'V* ', 'EB* ', '* ', 'SV* '.

    SIMBAD prepends a type designator followed by '* ' to many identifiers.
    VSX does not use this convention and will return no results for them.
    Example: 'V* SZ Lyn'  →  'SZ Lyn'
    """
    return re.sub(r"^[A-Za-z*]+\*\s+", "", star_id).strip()


def lookup_star(star_id: str) -> dict:
    vsx_id = _strip_simbad_prefix(star_id)

    # Cache is keyed on the normalised VSX identifier so that e.g. "V* SZ Lyn"
    # and "SZ Lyn" resolve to the same entry.
    cached = _load_cache(vsx_id)
    if cached:
        print(f"[cache] '{vsx_id}' loaded from {_cache_path(vsx_id)}", file=sys.stderr)
        return cached

    if vsx_id != star_id:
        print(f"Looking up '{star_id}' in VSX (as '{vsx_id}' — SIMBAD prefix stripped)...",
              file=sys.stderr)
    else:
        print(f"Looking up '{star_id}' in VSX...", file=sys.stderr)
    info = query_vsx(vsx_id)
    if info:
        print(f"[VSX] Found: {info['name']} ({info['type']})", file=sys.stderr)
        _save_cache(vsx_id, info)
        return info

    print(f"[VSX] Not found. Trying SIMBAD...", file=sys.stderr)
    info = query_simbad(star_id)
    if info:
        print(f"[SIMBAD] Found: {info['name']} ({info['type']})", file=sys.stderr)
        _save_cache(vsx_id, info)
        return info

    print(f"ERROR: Star '{star_id}' not found in VSX or SIMBAD.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Camera parameter interpolation
# ---------------------------------------------------------------------------

def get_camera_params(camera: str, gain: int) -> dict:
    """Interpolate camera parameters for the given gain (log-linear)."""
    db = CAMERA_DB[camera]
    cal = db["calibration"]
    gains_sorted = sorted(cal.keys())

    if gain <= gains_sorted[0]:
        e_per_adu, full_well, read_noise = cal[gains_sorted[0]]
    elif gain >= gains_sorted[-1]:
        e_per_adu, full_well, read_noise = cal[gains_sorted[-1]]
    else:
        # Find surrounding calibration points
        g_lo = max(g for g in gains_sorted if g <= gain)
        g_hi = min(g for g in gains_sorted if g > gain)
        e_lo, fw_lo, rn_lo = cal[g_lo]
        e_hi, fw_hi, rn_hi = cal[g_hi]

        # Log-linear interpolation
        t = (gain - g_lo) / (g_hi - g_lo)
        e_per_adu = math.exp(math.log(e_lo) + t * (math.log(e_hi) - math.log(e_lo)))
        full_well  = math.exp(math.log(fw_lo) + t * (math.log(fw_hi) - math.log(fw_lo)))
        read_noise = math.exp(math.log(rn_lo) + t * (math.log(rn_hi) - math.log(rn_lo)))

    adc_max = 2 ** db["adc_bits"] - 1
    sat_adu = min(full_well / e_per_adu, adc_max)

    return {
        "camera_name": db["name"],
        "sensor": db["sensor"],
        "adc_bits": db["adc_bits"],
        "pixel_size_um": db["pixel_size_um"],
        "e_per_adu": e_per_adu,
        "full_well_e": full_well,
        "read_noise_e": read_noise,
        "sat_adu": sat_adu,
    }


# ---------------------------------------------------------------------------
# Exposure calculation
# ---------------------------------------------------------------------------

def calc_exposure(
    mag: float,
    aperture_mm: float,
    focal_mm: float,
    obstruction: float,
    seeing_arcsec: float,
    airmass: float,
    pixel_size_um: float,
    e_per_adu: float,
    full_well_e: float,
    read_noise_e: float,
    sat_adu: float,
    target_fraction: float,
    sky_bg_mag_arcsec2: float,
    qe_peak: float,
    qe_avg: float,
) -> dict:
    """Return t_optimal and all intermediate quantities for a star of given magnitude."""

    # --- Photon flux (above atmosphere) ---
    # Vega-normalised: F0_V photons/s/m² for a V=0 star; each magnitude step
    # is a factor of 10^(1/2.5) ≈ 2.512 in flux.
    F_star = F0_V * 10 ** (-mag / 2.5)                   # photons/s/m²

    # --- Atmospheric extinction ---
    # Beer-Lambert in magnitude space: Δm = K × X, where X is airmass.
    F_ground = F_star * 10 ** (-K_EXT * airmass / 2.5)   # photons/s/m²

    # --- Collecting area (m²) ---
    # Annular aperture: subtract the central obstruction disc.
    aperture_m = aperture_mm / 1000.0
    A = math.pi / 4 * aperture_m ** 2 * (1 - obstruction ** 2)   # m²

    # --- Total photon rate reaching the sensor (no QE yet) ---
    # We keep photons and electrons separate because different Bayer pixels
    # have different QE. QE is applied only at the pixel level below.
    photon_rate = F_ground * A * T_OPTICS                 # ph/s (whole star, at sensor)

    # --- Total signal rate for display (using RGGB average QE) ---
    signal_rate_avg = photon_rate * qe_avg                # e⁻/s (approximate, whole star)

    # --- PSF peak pixel fraction ---
    # Model the PSF as a 2D Gaussian (good approximation for seeing-limited images).
    # The fraction of the total star flux that lands in one pixel depends on
    # how many pixels the star is spread across (σ in pixels).
    pixel_scale    = 206.265 * pixel_size_um / focal_mm                 # arcsec/pixel
    sigma_see_pix  = seeing_arcsec / (2.355 * pixel_scale)              # seeing σ in pixels
    FWHM_diff_arcsec = 1.22 * LAMBDA_V / (aperture_mm / 1000) * 206265 # Airy FWHM in arcsec
    sigma_diff_pix = FWHM_diff_arcsec / (2.355 * pixel_scale)          # diffraction σ in pixels
    sigma_pix      = math.sqrt(sigma_see_pix**2 + sigma_diff_pix**2)   # combined σ (quadrature sum)
    # Integrate a 2D Gaussian over a 1×1 pixel square centred on the peak.
    # For a symmetric Gaussian: integral = erf(0.5/(√2·σ))² (separable in x and y).
    _h = 0.5 / (math.sqrt(2.0) * sigma_pix)
    peak_frac      = math.erf(_h) ** 2                                  # fraction of star flux in peak pixel

    # --- Peak pixel signal rate ---
    # The peak pixel is a specific Bayer colour. In the worst case (most likely
    # to saturate first) it is green, which has the highest QE.
    # We apply qe_peak here so the saturation limit is conservative.
    peak_photon_rate = photon_rate * peak_frac            # ph/s landing on peak pixel
    peak_rate        = peak_photon_rate * qe_peak         # e⁻/s in the peak pixel

    # --- Target ADU and exposure time ---
    # We back-calculate the exposure that fills the peak pixel to target_fraction
    # of the saturation level (i.e. the safe headroom below clipping).
    target_adu = target_fraction * sat_adu                # ADU we aim for
    t_optimal  = target_adu * e_per_adu / peak_rate       # seconds

    # --- Sky background signal rate (per pixel) ---
    # Sky photons also pass through a Bayer filter; the peak pixel (green) sees
    # sky photons with qe_peak, not the average QE.
    F_sky_surface  = F0_V * 10 ** (-sky_bg_mag_arcsec2 / 2.5)  # photons/s/m²/arcsec²
    pixel_solid_angle = pixel_scale ** 2                         # arcsec²/pixel
    sky_photon_rate   = F_sky_surface * A * T_OPTICS * pixel_solid_angle  # ph/s/pixel
    sky_rate          = sky_photon_rate * qe_peak                          # e⁻/s/pixel (peak Bayer colour)

    # Sky-limited floor: the minimum useful exposure is where sky noise equals
    # read noise — below this, read noise dominates and adding more subs is
    # more efficient than lengthening the exposure.
    #   sky_noise = √sky_e = √(sky_rate · t)  and  read_noise = σ_read
    #   Setting equal: √(sky_rate · t_floor) = σ_read  →  t_floor = σ_read² / sky_rate
    t_sky_floor = read_noise_e ** 2 / sky_rate            # seconds

    # --- Metrics at the computed exposure ---
    peak_e          = peak_rate * t_optimal               # e⁻ in peak pixel from star
    peak_adu_actual = peak_e / e_per_adu
    sky_e           = sky_rate * t_optimal                # e⁻/pixel from sky

    # Full noise model: shot noise (star) + sky shot noise + read noise in quadrature.
    noise_shot_star = math.sqrt(peak_e)
    noise_shot_sky  = math.sqrt(sky_e)
    noise_read      = read_noise_e
    noise_total     = math.sqrt(peak_e + sky_e + read_noise_e ** 2)
    snr             = peak_e / noise_total

    return {
        "t_optimal": t_optimal,
        "peak_e": peak_e,
        "peak_adu": peak_adu_actual,
        "sat_fraction": peak_adu_actual / sat_adu,
        "signal_rate_avg": signal_rate_avg,
        "peak_photon_rate": peak_photon_rate,
        "peak_rate": peak_rate,
        "pixel_scale": pixel_scale,
        "pixel_solid_angle": pixel_solid_angle,
        "sigma_see_pix": sigma_see_pix,
        "sigma_diff_pix": sigma_diff_pix,
        "sigma_pix": sigma_pix,
        "peak_frac": peak_frac,
        "F_sky_surface": F_sky_surface,
        "sky_rate": sky_rate,
        "sky_e": sky_e,
        "t_sky_floor": t_sky_floor,
        "noise_shot_star": noise_shot_star,
        "noise_shot_sky": noise_shot_sky,
        "noise_read": noise_read,
        "noise_total": noise_total,
        "snr": snr,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_time(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds*1e6:.1f} µs"
    if seconds < 1.0:
        return f"{seconds*1000:.1f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}m {s:.1f}s"


def fmt_mag(m) -> str:
    return "N/A" if m is None else f"{m:.2f}"


def snr_rating(snr: float) -> str:
    """Return a quality label and approximate photometric precision for a given SNR.

    Thresholds are calibrated for peak-pixel SNR as computed by this script.
    Photometric precision ≈ 1/SNR (fractional), converted to magnitudes via
    Δm ≈ 2.5/ln(10) × (1/SNR) ≈ 1.086/SNR.

    These apply to the peak pixel; aperture photometry SNR will differ depending
    on how many pixels are summed.
    """
    #            SNR threshold   label        precision
    thresholds = [
        (200, "Excellent",  "< 5 mmag"),
        (100, "Good",       "~10 mmag"),
        ( 50, "Fair",       "~20 mmag"),
        ( 25, "Mediocre",   "~40 mmag"),
        ( 10, "Poor",       "~100 mmag"),
        (  5, "Bad",        "~200 mmag"),
        (  0, "Awful",      "> 200 mmag"),
    ]
    for threshold, label, precision in thresholds:
        if snr >= threshold:
            return f"{label}  ({precision})"
    return "Awful  (> 200 mmag)"


def hr(char="─", width=60):
    return char * width


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # 1. Star lookup
    star = lookup_star(args.star_id)

    # 2. Camera params
    cam = get_camera_params(args.camera, args.gain)

    # 3. Filter + sensor type — derive effective QE for the peak pixel
    filt = FILTER_DB[args.filter]
    sensor_type = CAMERA_DB[args.camera]["sensor_type"]

    if sensor_type == "mono":
        # Monochrome sensor: single QE value, no Bayer channel concept.
        # The combined sensor × filter QE is stored per filter in the camera entry.
        qe_peak = CAMERA_DB[args.camera]["qe_per_filter"][args.filter]
        qe_avg  = qe_peak
        qe_peak_channel = "mono"
    else:
        # OSC (colour) sensor: per-channel Bayer QE from the filter database.
        qe = filt["qe_channels"]
        qe_peak_channel = max(qe, key=qe.get)   # Bayer channel that saturates first
        qe_peak = qe[qe_peak_channel]
        qe_avg  = (qe["R"] + 2 * qe["G"] + qe["B"]) / 4  # RGGB-weighted mean

    # 4. Calculate at max brightness (worst case for saturation)
    mag_bright = star["mag_max"]
    res_bright = calc_exposure(
        mag=mag_bright,
        aperture_mm=args.aperture,
        focal_mm=args.focal_length,
        obstruction=args.obstruction,
        seeing_arcsec=args.seeing,
        airmass=args.airmass,
        pixel_size_um=cam["pixel_size_um"],
        e_per_adu=cam["e_per_adu"],
        full_well_e=cam["full_well_e"],
        read_noise_e=cam["read_noise_e"],
        sat_adu=cam["sat_adu"],
        target_fraction=args.target_saturation,
        sky_bg_mag_arcsec2=args.sky_background,
        qe_peak=qe_peak,
        qe_avg=qe_avg,
    )

    # 5. Calculate at min brightness (informational)
    res_faint = None
    if star["mag_min"] is not None:
        res_faint = calc_exposure(
            mag=star["mag_min"],
            aperture_mm=args.aperture,
            focal_mm=args.focal_length,
            obstruction=args.obstruction,
            seeing_arcsec=args.seeing,
            airmass=args.airmass,
            pixel_size_um=cam["pixel_size_um"],
            e_per_adu=cam["e_per_adu"],
            full_well_e=cam["full_well_e"],
            read_noise_e=cam["read_noise_e"],
            sat_adu=cam["sat_adu"],
            target_fraction=args.target_saturation,
            sky_bg_mag_arcsec2=args.sky_background,
            qe_peak=qe_peak,
            qe_avg=qe_avg,
        )

    # 6. Print results
    W = 60
    print()
    print(hr("═", W))
    print(f"  Variable Star Optimal Exposure Calculator")
    print(hr("═", W))

    print()
    print("  STAR")
    print(hr())
    print(f"  Name      : {star['name']}")
    print(f"  Type      : {star['type']}")
    print(f"  Source    : {star['source']}")
    if star["period"]:
        print(f"  Period    : {star['period']} days")
    print(f"  Mag range : {fmt_mag(star['mag_max'])} (bright) → {fmt_mag(star['mag_min'])} (faint)")

    print()
    print("  CAMERA & SENSOR")
    print(hr())
    print(f"  Camera    : {cam['camera_name']} ({cam['sensor']})")
    print(f"  ADC bits  : {cam['adc_bits']}-bit  (max {2**cam['adc_bits']-1} ADU)")
    print(f"  Gain      : {args.gain}  (e⁻/ADU = {cam['e_per_adu']:.3f})")
    print(f"  Offset    : {args.offset}")
    print(f"  Full well : {cam['full_well_e']:.0f} e⁻")
    print(f"  Read noise: {cam['read_noise_e']:.2f} e⁻")
    print(f"  Sat. ADU  : {cam['sat_adu']:.0f}  (target {args.target_saturation*100:.0f}% = {args.target_saturation*cam['sat_adu']:.0f} ADU)")

    print()
    print("  FILTER")
    print(hr())
    print(f"  Filter    : {filt['name']}")
    if sensor_type == "mono":
        print(f"  Eff. QE   : {qe_peak:.2f}  (monochrome — sensor QE × filter transmission)")
    else:
        qe = filt["qe_channels"]
        print(f"  Eff. QE   : R={qe['R']:.2f}  G={qe['G']:.2f}  B={qe['B']:.2f}  "
              f"(RGGB avg={qe_avg:.2f})")
        print(f"  Peak pixel: {qe_peak_channel} channel  (QE={qe_peak:.2f})  ← first to saturate")
    if filt["photometry_note"]:
        print(f"  ⚠  {filt['photometry_note']}")

    print()
    print("  TELESCOPE & CONDITIONS")
    print(hr())
    print(f"  Aperture  : {args.aperture:.0f} mm")
    print(f"  Focal len : {args.focal_length:.0f} mm  (f/{args.focal_length/args.aperture:.1f})")
    print(f"  Pixel scale: {res_bright['pixel_scale']:.2f} arcsec/pixel  [206.265 × pixel_size / focal_length]")
    print(f"               how many arcsec of sky one pixel subtends")
    if args.obstruction > 0:
        print(f"  Obstruction: {args.obstruction*100:.0f}%")
    print(f"  Seeing    : {args.seeing:.1f} arcsec FWHM")
    print(f"    σ_seeing  = {res_bright['sigma_see_pix']:.2f} px  [FWHM / (2.355 × pixel_scale)]")
    print(f"               atmospheric blur expressed as Gaussian σ; 2.355 = 2√(2 ln 2) links FWHM to σ")
    print(f"    σ_diff    = {res_bright['sigma_diff_pix']:.2f} px  [1.22 λ/D × 206265 / (2.355 × pixel_scale)]")
    print(f"               diffraction Airy disc — irreducible blur set by aperture and wavelength")
    print(f"    σ_eff     = {res_bright['sigma_pix']:.2f} px  [√(σ_seeing² + σ_diff²)]")
    print(f"               both blur sources are independent, so their variances add (quadrature sum)")
    print(f"    Peak frac = {res_bright['peak_frac']*100:.2f}%  [erf(0.5/(√2·σ_eff))²]")
    print(f"               fraction of total star flux falling in the single brightest pixel;")
    print(f"               sharper PSF (smaller σ) → higher fraction → pixel saturates faster")
    print(f"  Airmass   : {args.airmass:.2f}")

    print()
    print("  SKY BACKGROUND")
    print(hr())
    print(f"  Input           : {args.sky_background:.2f} mag/arcsec²")
    print(f"  Surface flux    : {res_bright['F_sky_surface']:.3e} ph/s/m²/arcsec²  [F₀ × 10^(−sky/2.5)]")
    print(f"                    sky glow is a dim extended source — same Pogson formula as for stars")
    print(f"  Pixel solid ang : {res_bright['pixel_solid_angle']:.3f} arcsec²/pixel  [pixel_scale²]")
    print(f"                    area of sky seen by one pixel; bridges surface brightness → per-pixel flux")
    print(f"  Sky rate        : {res_bright['sky_rate']:.3f} e⁻/s/pixel  [F_sky × A × T_optics × QE_peak × Ω_pix]")
    print(f"                    sky electrons per second in the peak-colour pixel — sets the noise floor")
    print(f"  Sky-limited floor: {fmt_time(res_bright['t_sky_floor'])}  [σ_read² / sky_rate]")
    print(f"                    below this exposure sky noise < read noise; longer exposures are more efficient")

    print()
    print("  SIGNAL CHAIN — AT MAXIMUM BRIGHTNESS (mag {:.2f})".format(mag_bright))
    print(hr())
    print(f"  Star flux (above atm) : {F0_V * 10**(-mag_bright/2.5):.3e} ph/s/m²  [F₀ × 10^(−mag/2.5)]")
    print(f"                          Pogson's law: each magnitude step is a factor of 2.512 in flux")
    ext_factor = 10 ** (-K_EXT * args.airmass / 2.5)
    print(f"  After extinction      : ×{ext_factor:.4f}  [10^(−K·X/2.5), K={K_EXT}, X={args.airmass:.2f}]")
    print(f"                          atmosphere absorbs K mag per airmass unit; X = sec(zenith angle)")
    A_bright = math.pi / 4 * (args.aperture / 1000) ** 2 * (1 - args.obstruction ** 2)
    print(f"  Collecting area       : {A_bright:.4f} m²  [π/4 · D² · (1 − obs²)]")
    print(f"                          annular aperture area; central obstruction reduces it quadratically")
    print(f"  Total signal rate     : {res_bright['signal_rate_avg']:.1f} e⁻/s  [flux × A × T_optics={T_OPTICS} × QE_avg={qe_avg:.2f}]")
    print(f"                          photons through the full optical chain converted to electrons (all pixels)")
    print(f"  Peak photon rate      : {res_bright['peak_photon_rate']:.2f} ph/s  [total_photons × peak_frac={res_bright['peak_frac']*100:.2f}%]")
    print(f"                          only the fraction landing on the single brightest pixel matters for saturation")
    print(f"  Peak pixel rate       : {res_bright['peak_rate']:.2f} e⁻/s  [peak_photons × QE_{qe_peak_channel}={qe_peak:.2f}]")
    if sensor_type == "mono":
        print(f"                          monochrome sensor — all pixels identical, QE={qe_peak:.2f}")
    else:
        print(f"                          {qe_peak_channel} channel has highest QE through this filter → saturates first")

    print()
    print("  RESULTS — AT MAXIMUM BRIGHTNESS (mag {:.2f})".format(mag_bright))
    print(hr("═", W))
    t = res_bright["t_optimal"]
    print(f"  ★ Recommended exposure : {fmt_time(t)}")
    print(f"    [target_ADU × e⁻/ADU / peak_rate  =  {args.target_saturation:.0%} × {cam['sat_adu']:.0f} × {cam['e_per_adu']:.3f} / {res_bright['peak_rate']:.2f}]")
    print(f"     work backwards: how long until the peak pixel reaches the target fill level?")
    print()
    print(f"    Star peak pixel  : {res_bright['peak_e']:.1f} e⁻  →  {res_bright['peak_adu']:.0f} ADU  ({res_bright['sat_fraction']*100:.1f}% of saturation)")
    print(f"    Sky per pixel    : {res_bright['sky_e']:.1f} e⁻  →  {res_bright['sky_e']/cam['e_per_adu']:.1f} ADU")
    print()
    print(f"    Noise budget (e⁻ rms):")
    print(f"      Star shot noise : √{res_bright['peak_e']:.1f}  = {res_bright['noise_shot_star']:.1f} e⁻   (Poisson: variance = signal)")
    print(f"      Sky shot noise  : √{res_bright['sky_e']:.2f} = {res_bright['noise_shot_sky']:.2f} e⁻   (same Poisson statistics for sky)")
    print(f"      Read noise      :          {res_bright['noise_read']:.2f} e⁻   (fixed per exposure, from electronics)")
    print(f"      Total (quadrature): {res_bright['noise_total']:.1f} e⁻  [√(shot² + sky² + read²)  — independent noise sources add in quadrature]")
    print()
    print(f"    SNR (peak pixel) : {res_bright['snr']:.1f}  → {snr_rating(res_bright['snr'])}")
    print(f"                       [star_e / total_noise  — how many σ above the noise floor the star sits]")
    print()
    sky_floor_flag = "OK — sky-limited" if t >= res_bright["t_sky_floor"] else "below sky-limited floor — consider longer exposures"
    print(f"    Sky-limited floor: {fmt_time(res_bright['t_sky_floor'])}  →  {sky_floor_flag}")

    if t < 0.05:
        print()
        print("  ⚠  WARNING: Exposure < 50 ms — this star may be too bright")
        print("     for your aperture. Consider a smaller scope, ND filter,")
        print("     narrowband filter, or imaging at minimum brightness only.")

    if res_faint is not None:
        mag_faint = star["mag_min"]
        # Use the bright-derived exposure to show what faint looks like
        peak_e_faint_at_bright_t = res_faint["peak_rate"] * t
        sky_e_faint_at_bright_t  = res_faint["sky_rate"] * t
        peak_adu_faint = peak_e_faint_at_bright_t / cam["e_per_adu"]
        noise_faint = math.sqrt(
            peak_e_faint_at_bright_t + sky_e_faint_at_bright_t + cam["read_noise_e"] ** 2
        )
        snr_faint = peak_e_faint_at_bright_t / noise_faint
        print()
        print("  AT MINIMUM BRIGHTNESS (mag {:.2f})  — same {} exposure".format(
            mag_faint, fmt_time(t)))
        print(hr())
        print(f"    Star peak pixel  : {peak_e_faint_at_bright_t:.1f} e⁻  →  {peak_adu_faint:.0f} ADU  ({peak_adu_faint/cam['sat_adu']*100:.1f}% of saturation)")
        print(f"    Sky per pixel    : {sky_e_faint_at_bright_t:.1f} e⁻  (unchanged)")
        print(f"    SNR (peak pixel) : {snr_faint:.1f}  → {snr_rating(snr_faint)}")

        delta_mag = mag_faint - mag_bright
        flux_ratio = 10 ** (delta_mag / 2.5)
        print(f"    Flux ratio (faint/bright): {flux_ratio:.1f}×  (Δ{delta_mag:.1f} mag)")

    print()
    print(hr("═", W))
    print()


if __name__ == "__main__":
    main()
