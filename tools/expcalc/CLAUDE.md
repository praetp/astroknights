# varstar_exp — Variable Star Exposure Calculator

## Setup
First-time setup (creates `.venv` and installs all dependencies):
```
bash setup.sh
source .venv/bin/activate
```

## Self-test
After every code change, run (venv must be active):
```
python3 varstar_exp.py "V* SZ Lyn"
```
This star exercises the SIMBAD prefix stripping, VSX lookup, Bayer QE logic, and full output formatting.

## Permissions
`python3 varstar_exp.py` and `bash setup.sh` are always allowed — never ask for confirmation.
