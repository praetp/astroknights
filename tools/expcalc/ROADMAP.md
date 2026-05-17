# varstar_exp — Roadmap

## Planned

### Defocus support
Add `--defocus <arcsec>` parameter specifying the desired defocused disc diameter.
Switches the PSF model from a Gaussian (seeing-limited) to a uniform disc, using
peak fraction ≈ 1 / (π · R²) where R is the disc radius in pixels.
Motivation: deliberate defocus spreads stellar flux over more pixels, preventing
saturation on bright targets and extending the accessible dynamic range — a standard
technique in variable star photometry.
