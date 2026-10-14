# Implementation execution record

## October 14, 2026: I01 started

Destination workspace: `R:\Users\Zach\Documents\GitHub\CustomRaceModule`; product name `mod-esteria-races`.
This is already a separate Git repository. No second repository, remote, publication or deployment was created.

Implemented:

- `tools/racepack/baseline.py`: parameterized read-only source/runtime capture, exact upstream reference
  fetch, PE architecture probe, historical export comparison, canonical lock digest, missing-input report,
  private capture context and completion marker. Rejects existing/overlapping output roots and escaping inputs.
- `tools/racepack/verify_baseline.py`: full frozen-file readback, sizes/hashes, lock digest and capture marker;
  rejects modified, incomplete, duplicate and unsafe evidence keys.
- `tests/unit/`: evidence-integrity, immutable destination, canonical digest and PE validation cases.
- `release/baseline.lock.json`: fresh portable hash ledger, selected development pins and open gaps.
- `docs/implementation/`: preserved normative package with links to original supporting evidence.

Private frozen bundle (outside Git):
`R:\Users\Zach\Documents\GitHub\CustomRaceModule-evidence\2026-10-14-initial`.
Its `capture-context.private.json` holds local paths and the source worktree listing; do not publish the
bundle wholesale. No credentials, WTF, SavedVariables or personal DB records were requested for capture.
Payload provenance/distribution audit remains open. The Git listing was unchanged before/after capture;
that check does not establish an atomic live-system snapshot or a source-to-server-image match.

Input digest: `b5b34dc27e6d2084efdf336e1ca1bae012aa33871855afe90140ba7fbdcd2c19`.
The lock embeds individual frozen hashes and versions. Original October inventories were preserved.

Checks executed: `rtk proxy python -m unittest discover -s tests/unit -v` passed all seven cases;
`rtk proxy python -m tools.racepack.verify_baseline <bundle>` verified all 287 frozen files and the lock
digest. No CMake configure, C++ build, DB command, service action, client patch or live scenario was run.

I01 remains **in progress**. Its checkbox remains unchecked. A follow-up read-only runtime probe now
records the recognized enUS/root archive chain, explicitly flags unclassified MPQs, captures the running
`ac-worldserver` image identity and worldserver SHA-256, and records only race-data mount destinations.
The current server mounts ten race-relevant DBC/continuation destinations read-only; bind source paths,
Docker environment, credentials and character rows are deliberately excluded. The observation is stored in
`release/runtime-observation.json`, and `tools/racepack/probe.py` reproduces it without mutating targets.

The recognized client resolver sees 52 archives and places `Data/enUS/patch-enUS-Z.MPQ` above the root
`Data/patch-Z.MPQ`. Five MPQs remain unclassified by the stock letter/number resolver and therefore block
claiming complete effective archive order: `common-3.MPQ`, locale `backup-enUS.MPQ`, `Patch-Dn.MPQ`,
`Patch-Dr.MPQ` and `Patch-Zzz.mpq`. The running worldserver binary SHA-256 is
`5f7cf86777a170f2bc73b72af1967aea19f2cceb8e790723eccf31262ba52b94`; its Docker image ID is
`sha256:5fef573b2c458fb954c06c1c5f694e3d0c1e3fc40f28b02fd803ad503d95bd94`.

A second read-only pass resolved and hashed seven race-critical effective client DBCs plus the current
GlueXML TOC and nine key login/create/select Glue files. All of those entries currently resolve from
`Data/enUS/patch-enUS-Z.MPQ`. Matching live server hashes were captured for the mounted race DBC set.
`CharStartOutfit.dbc` and `CreatureDisplayInfo.dbc` match client/server byte-for-byte; `ChrRaces.dbc`,
`CharSections.dbc`, `BarberShopStyle.dbc`, `CreatureModelData.dbc` and `Spell.dbc` differ and must be treated
as explicit reconciliation inputs rather than assumed drift.

The live character schema was also inspected read-only. `race`, the five stock appearance bytes and
`gender` are `TINYINT UNSIGNED`; `extraAppearance` is already `BIGINT UNSIGNED`. Aggregate counts by RaceID
were captured without GUIDs, names or account identifiers. Only saved races 48 and 51 currently have nonzero
`extraAppearance` values, so those codec meanings must be frozen before any I02 remap or generated registry.

A source/import foundation now exists for the next extraction stages. `tools/racepack/wowio/` vendors the
portable dependency-free MPQ reader/writer and effective archive resolver. `tools/racepack/import_esteria.py`
and `data/vendor/esteria-import.json` define strict path-scoped imports for race manifests/registry, native
appearance/select source, server appearance/racial source, startup database reference data, legacy race tools,
effective Glue dependencies and optional loose runtime candidates. Writes are hash-verified and refuse a
changed destination unless `--replace` is explicit.

A real-client staging run captured 156 source/reference files, 74 Interface dependencies and 9 static Glue
assets with zero unresolved static asset literals. Adding the current native runtime candidates contributes
42 more files and brings that staging tree to roughly 300 MB. Runtime candidates remain marked for
redistribution/provenance review instead of being silently committed. The five unclassified MPQs are still
reported as a warning, so this does not certify final archive precedence.

The repository now directly preserves three byte-exact Esteria inputs under source-lock control: current
`allocation.json`, current `race_registry.json`, and the winning `GlueXML.toc`. Their SHA-256 values are
checked by unit tests. Raw files under `vendor/esteria/` remain evidence, not the I02 reconciled identity
contract.

Authoritative handling of the five unclassified archives, complete transitive model/texture/audio closure,
owned startup/racial live SQL state, verified stock client provenance, exact source-to-runtime revision
correspondence, runtime redistribution provenance and a concrete Linux compiler version remain missing.

## October 14, 2026: I02 started and module skeleton added

The repository now has a modern AzerothCore module skeleton under `src/` plus
`conf/mod_esteria_races.conf.dist`. It targets installation as `modules/mod-esteria-races`, whose generated
loader calls `Addmod_esteria_racesScripts()`. The development module defaults disabled and does not enable
custom race behavior until a reconciled identity policy and matching pinned core adapter exist. No CMake
configure/build was run.

I02 began from effective client/server ChrRaces, current Glue metadata, current registry/manifests, core enum
claims and aggregate saved RaceID evidence. `release/identity-reconciliation.json` and
`docs/compatibility/identity-reconciliation.md` now preserve the first safe decisions and blockers. Races 29,
30 and 31 are retained as Kul Tiran Alliance, Illidari Horde and Illidari Alliance because current client/Glue
identity agrees and saved characters exist. Race 62 remains the active Sethrak; legacy ID 15 remains
non-playable. Race 61 remains Alliance Ogre and the stale Furbolg claim is rejected; race 71 is recorded only
as an observed-free candidate pending complete ownership/allocation checks.

The reconciliation also exposes two hard blockers rather than hiding them: IDs 24-27 disagree between the
effective ChrRaces tables and older registry/core definitions, and IDs 66/67 disagree between Drakkin client/
Glue/manifests and Kobold server ChrRaces naming. Race 66 has a saved character and therefore cannot be
silently reinterpreted. Existing extended-appearance values on races 48 and 51 are explicit codec-freeze
requirements.

I01 and I02 remain **in progress**; I03–I15 have not started. No selected or `all` release can pass the
current gates.
