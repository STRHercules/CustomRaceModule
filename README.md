# mod-esteria-races

A dedicated AzerothCore custom-race distribution under development in the
`CustomRaceModule` repository. The target includes selectable race packs, the complete Esteria Glue UI,
independent branding, and matched server/client support for 100 characters.

Implementation began October 14, 2026 with I01, the baseline-capture tools. There is no installable server
module, core adapter, client installer, or supported release yet. No existing Esteria installation was changed.

Read the [implementation package](docs/implementation/custom-race-module.INDEX.md),
[initial compatibility targets](docs/compatibility/initial-targets.md), and
[execution record](docs/implementation/progress.md). Original analysis and inventories remain in `docs/`.

Read-only developer commands from this repository:

```powershell
rtk proxy python -m tools.racepack.baseline --help
rtk proxy python -m tools.racepack.verify_baseline '<external-bundle-directory>'
rtk proxy python -m unittest discover -s tests/unit -v
```

Capture requires explicit source/client/output roots, a full upstream SHA, and a compiler target version.
Output must be a new directory outside the module and all declared input roots. Private frozen payloads
stay outside Git; `release/baseline.lock.json` contains hashes, relative evidence keys, and explicit gaps.
Capture discovers executable candidates but never patches them or marks them supported.

Do not run the historical `docs/custom-race-module.capture.py` from its relocated path: its inferred
source root and workstation paths belong to the old planning location. Use the parameterized tool above.
