# mod-custom-races

A standalone AzerothCore WotLK custom-race distribution under development. The public module has no
CoA, Ascension, repack, server-manager or playerbots requirement. Esteria is a content provider and
migration profile. The target includes selectable race packs, the complete adapted Glue UI, replaceable
branding, and matched server/client support for 100 characters.

The [CoA reference comparison](docs/compatibility/coa-reference.md) records the pinned branch,
verified module/core/client split and the current general-server product direction.

**Current status: source foundation, not a playable custom-race release.** Neutral loader/config,
actual-ID admission policy, deterministic generation and source staging/installation exist. The installed
identity set remains empty while reconciliation is incomplete. The core adapter and matched client/data
release remain unimplemented. Full AzerothCore compilation has not been verified.

Source installation into a separate upstream checkout pinned at `aa8a04c82ffc315277e93e937b4e6a0d7a6aba58`:

```powershell
rtk proxy python -m tools.racepack inspect-core --core-root '<azerothcore-checkout>'
rtk proxy python -m tools.racepack install-module --core-root '<azerothcore-checkout>'
rtk proxy python -m tools.racepack stage-module --output '<new-offline-source-directory>'
```

The installer checks core revision and hook/loader hashes, refuses conflicting/existing modules and
creates `modules/mod-custom-races`. It runs no build, SQL or client installation. Read the
[source installation instructions](docs/installation/source-module.md) before building with the host core.

Policy checks:

```powershell
rtk proxy python -m tools.racepack generate-policy --check
rtk proxy cmake -S tests/native -B build/native-policy
rtk proxy cmake --build build/native-policy --config Release
rtk proxy ctest --test-dir build/native-policy -C Release --output-on-failure
```

The native harness tests the standalone admission policy, not the AzerothCore module.

Implementation began October 14, 2026 with I01 baseline capture, portable source/import tooling and
I02 identity reconciliation. Frozen snapshots and existing evidence locks retain their original names
and hashes. No existing Esteria installation was changed.

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

Install as `modules/mod-custom-races` so the modern loader calls `Addmod_custom_racesScripts()`.
The supplied configuration defaults `CustomRaces.Enable = 0`. Enabling this source foundation cannot
activate custom races until the reconciled policy and matched core/client/data work is complete.
The old module directory/config name is retired for new installations; do not install both names.

Do not run the historical `docs/custom-race-module.capture.py` from its relocated path: its inferred
source root and workstation paths belong to the old planning location. Use the parameterized tool above.
