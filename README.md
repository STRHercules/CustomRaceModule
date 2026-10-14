# mod-esteria-races

A dedicated AzerothCore custom-race distribution under development in the
`CustomRaceModule` repository. The target includes selectable race packs, the complete Esteria Glue UI,
independent branding, and matched server/client support for 100 characters.

Implementation began October 14, 2026 with I01 baseline capture and has expanded into the portable source/import
foundation, a safe AzerothCore module skeleton, and I02 identity reconciliation. There is no supported release,
core adapter, or client installer yet. No existing Esteria installation was changed.

Read the [implementation package](docs/implementation/custom-race-module.INDEX.md),
[initial compatibility targets](docs/compatibility/initial-targets.md), and
[execution record](docs/implementation/progress.md). Original analysis and inventories remain in `docs/`.

Read-only developer commands from this repository:

```powershell
rtk proxy python -m tools.racepack.baseline --help
rtk proxy python -m tools.racepack.verify_baseline '<external-bundle-directory>'
rtk proxy python -m tools.racepack.probe --client-root '<client-root>' --server-container ac-worldserver
rtk proxy python -m tools.racepack.import_esteria --source-root '<EsteriaWoW>' --client-root '<client>' --output-root '<staging>'
rtk proxy python -m unittest discover -s tests/unit -v
```

Baseline capture requires explicit source/client/output roots, a full upstream SHA, and a compiler target version.
Output must be a new directory outside the module and all declared input roots. Private frozen payloads stay
outside Git; `release/baseline.lock.json` contains hashes, relative evidence keys, and explicit gaps.

The repository now also owns a dependency-free MPQ/client resolver, a strict Esteria import contract, exact raw
allocation/registry evidence, and the current winning Glue TOC. See `docs/development/esteria-import.md` before
adding more source/runtime assets. Runtime binaries and large generated catalogs remain provenance-gated.

When testing as an AzerothCore module, the checkout must be installed under the module directory name
`modules/mod-esteria-races` so the generated modern loader calls `Addmod_esteria_racesScripts()`. The supplied
configuration defaults `EsteriaRaces.Enable = 0`; enabling the current development skeleton still does not
activate custom race behavior until the reconciled policy/core adapter work is complete.

Do not run the historical `docs/custom-race-module.capture.py` from its relocated path: its inferred
source root and workstation paths belong to the old planning location. Use the parameterized tool above.
