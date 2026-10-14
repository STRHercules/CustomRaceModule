# mod-esteria-races ordered implementation plan

Execute against [REQUIREMENTS](custom-race-module.REQUIREMENTS.md),
[DESIGN](custom-race-module.DESIGN.md) and [EXTRACTION](custom-race-module.EXTRACTION.md).
I01 is **in progress**; I02–I15 are **not started**. See [execution record](progress.md).
Proposed output paths are in the new repository unless qualified.
Creating these documents does not mean their code/artifacts exist. No time estimates replace done criteria.

## Execution rules and delivery checkpoints

Work in an isolated new module workspace and isolated server/client fixtures. Keep the live Esteria
installation unchanged until I15's explicit migration deployment. Use current matching sources and
verified receipts, not stale copied runtime sets. Preserve existing working changes/untracked files.
Develop new SQL under this repository's approved pending directories when working here; never modify
its immutable base/archive/merged SQL. Follow the new repository's conventions after extraction.

Before later implementation, read applicable C++/script/SQL/subsystem guidance. Before a configure,
build or test, read `.agents/docs/build.md`; builds/configuration require explicit authorization in
Esteria. Before submission self-review, read the required review/self-review docs. These steps are future
implementation instructions; this document-creation task does not execute builds or test suites.

Milestones:

- M1: I01–I04 establish one reconciled source/data/asset contract and the schema foundations.
- M2: I05–I10 produce a minimal server adapter, guarded runtime and complete Glue/capacity implementation.
- M3: I11–I13 produce a selective installer and representative isolated end-to-end pilot.
- M4: I14 promotes all in-scope races/profiles/assets and packages the complete offline release.
- M5: I15 migrates Esteria with saved-character preservation after separately authorized deployment.

Dependency order:

```text
I01 -> I02 -> I03 -> I04
I03 -> I05 -> I06 -> I07
I01 + I03 + I04 -> I08 -> I09 -> I10
I04 + I07 + I08 + I09 + I10 -> I11 -> I12 -> I13 -> I14 -> I15
```

I04 can accumulate asset evidence while adapter work proceeds; no generated release may bypass its
complete-closure gate. Independent workstreams are not a request to spawn agents; use normal task execution.

## I01 — Freeze inputs and compatibility targets

- [ ] Status: in progress; frozen source/runtime evidence and upstream pin captured, effective/live gaps open.
  Requirements: R02, R14. Dependency: none.

Read existing analysis/inventory and extract current source/runtime/server evidence per E01–E07.
Choose and record the first upstream AC commit SHA and supported toolchain versions. Identify stock
client image candidates, active Esteria image/patch chain, WXL source/vendor provenance and actual
effective root/locale/server data. Compare dirty source to the running image without equating them.
Capture aggregate saved race/codec state read-only for reconciliation; keep private migration data private.

Outputs: `docs/compatibility/initial-targets.md`, `release/baseline.lock.json`, frozen evidence bundle
external to Git, and an input availability/provenance report. Record missing foundation/tool sources
as concrete acquisition/adaptation tasks in I08, not as permission to weaken validation.

Done: source inputs/outputs are reproducibly identified; pinned upstream/toolchain values are concrete;
no active files/services/databases changed. Fresh hashes replace assumptions about the October export.

## I02 — Reconcile the full identity ledger

- [ ] Status: not started. Requirements: R01, R07, R08, R12. Dependency: I01.

Reconcile registry, allocation, enum, effective ChrRaces/SQL/UI and saved identities. Resolve cases in
E01, including 24–27, 29–31/67 omissions, 15/62 Sethrak, 61 Ogre/Furbolg, newer Naga/Vrykul and shared
Kobold gender bodies. Keep Furbolg in scope under a free distinct identity after conflict checks.
Separate species/faction keys, donor/visual/model identities, creator ordinal and NPC reservations.
Specify class/gender/creator visibility/default/start/racial policy and codec version for every identity.

Outputs: `data/registry/{species,identities,allocations}.json`, `docs/compatibility/identity-reconciliation.md`,
`release/identity-reconciliation.json`, target-specific migration requirements and unresolved flags.

Done: each current custom family has one unambiguous stable identity contract. No existing character is
silently reassigned. `all` cannot hide conflicts by dropping entries; unresolved items block that release.

## I03 — Implement strict schemas, locks and shared generation foundation

- [ ] Status: not started. Requirements: R07, R08, R10, R14. Dependencies: I01, I02.

Create the isolated module skeleton without configuring/building unless authorized. Match pinned loader/
CMake/config conventions and preserve licenses. Implement DESIGN schemas, canonical digests, strict
loaders and a path-safe artifact store. Port frozen appearance choice/codec data into versioned inputs.
Implement allocation and dependency resolution with exact ownership/conflict predicates and shared owners.
Generate one common identity/codec definition set for both runtimes; remove divergent copied definitions.

Outputs: module skeleton, `schemas/`, `tools/racepack/{models,canonical,resolve,artifacts}.py`,
`shared/generated/`, species manifest/choice inputs, lock validation fixtures.

Done: identical semantic inputs produce identical generated definitions/digests; invalid capacity,
duplicate owner, out-of-range choice, unsupported version and unsafe path are rejected. Old codecs are
round-trip equivalent. Operator paths/credentials never leak into portable artifacts or stable hashes.

## I04 — Capture every required asset and dependency

- [ ] Status: not started. Requirements: R03, R04, R13, R14. Dependencies: I01–I03.

Refactor export/resolver/packer recipes into parameterized read-only capture services. Build per-race
and shared dependency graphs from models/DBC/catalog/Glue/addon roots, including dynamically constructed
paths, all supported choices, animation inheritance, equipment, portraits, sounds and current scenes.
Resolve dependencies currently provided by other custom patches into actual payload bytes. Classify
historical missing references by reachability and repair every reachable gap; do not fabricate assets.
Track provenance, required capabilities and shared ownership in the per-file ledger.

Outputs: external immutable `packs/{shared,races}/` payload roots, `release/asset-ledger.json`,
`release/extraction-ledger.json`, capture recipes and missing-reference reports.

Done: all scoped non-stock dependencies have captured/generated bytes; stock dependencies resolve on
the declared clean baseline. No required runtime reads G:/R:/C: development paths or donor archives.
Full UI assets remain included for subsets. Asset byte checks are recorded separately from live acceptance.

## I05 — Extract module scripts, startup and exact-race policy

- [ ] Status: not started. Requirements: R07, R09, R12, R15. Dependency: I03.

Split Broken/Darkfallen/Worgen scripts and data per E03, preserving behavior and script names/bindings
where required. Implement installed/creation-enabled/retained actual-ID policy, per-race class/gender
validation and diagnostics. Convert startup export evidence into scoped recipes: starts, actions/items,
skills/spells/languages/exclusions, stat/totem/form/racial requirements. Keep host progression foreign-owned.
Do not register the same racial twice through the old and new modules in the future migration.

Outputs: `src/Race{Policy,Startup,Diagnostics}.*`, `src/racials/`, generated registrations/config,
`data/races/*/startup.json`, shared schema recipes and owned bindings.

Done: selected and retained identities are explicit; donor-only dependencies do not become playable.
No larger custom-server/classless module is required for extracted race behavior. Accurate tooltip/racial
profiles describe actual implementations. All foreign-row replacements require an explicit conflict plan.

## I06 — Implement the minimal pinned AC adapter

- [ ] Status: not started. Requirements: R02, R07–R10, R15. Dependencies: I01, I03, I05.

Produce the file/hunk matrix in E02 against the pinned upstream revision. Finalize early registration/
initialization order and bridge signatures; add only missing race extension points. Port dynamic race
capacity, bounded donor eligibility call sites, exact-race startup and selected identity checks.
Add appearance create/enum/storage/update-field integration with generated definitions. Preserve stock
fallback and detect foreign padding/protocol conflicts. Do not use the broad historical core patch.

Outputs: `integration/acore/<sha>/{custom-races.patch,compatibility.json,hunk-map.json}`, bridge API,
core contract checks/fixtures and `docs/compatibility/core-adapter.md`.

Done: checked patch applies to the exact pinned input and rejects conflicting revisions. Every hunk
has a requirement/test and excludes unrelated Esteria behavior. An authorized isolated build confirms
the module/core linkage and startup order; until then record source-complete, not compiled/accepted.

## I07 — Implement owned data generation and appearance migrations

- [ ] Status: not started. Requirements: R08–R12, R14. Dependencies: I03, I05, I06.

Generate full target-effective client/server DBCs from row deltas and allocation locks. Validate string
pools/references/order and preserve intentional client/server skill eligibility differences. Generate
selected SQL with scoped ownership and before-images, separate shared updater schema from optional seeds.
Preserve current schema when a five-byte-only selection needs no extension. Six-byte/uint64 selections
use compatible extraAppearance migration and prepared statements. Implement old→stable-choice→new codec
migration only when required, scoped to target characters; never replay historical GUID migrations.

Outputs: `tools/racepack/{dbc,sql,migrate}.py`, migration recipes, before/after row artifacts, isolated
schema/data/persistence fixtures and upgrade compatibility descriptions.

Done: deterministic target merges preserve foreign rows, sorted CharSections and frozen bytes; malformed
data and unsafe schema downgrade are rejected. Scoped row writes/DDL recovery are separately tracked.

## I08 — Make native runtime and executable profiles portable

- [ ] Status: not started. Requirements: R02, R03, R06, R08, R14. Dependencies: I01, I03, I04.

Vendor/pin source and required runtime dependency graph; replace absolute build paths. Preserve current
DLL/catalog ABI and 129-slot guards. Recover the clean-client foundation transformation or implement
a separately validated stock-12340 backend. Compose guarded foundation/appearance/character-limit/
archive repair steps from known hashes. Detect loader/proxy conflicts and already-applied outputs.
Refactor race-ID switches to generated mappings; carry lifetime/material/AL/stdcall repairs forward.

Outputs: `client/native/`, `client/profiles/12340/`, `native-abi.json`, patch engine/fixtures, matched
Win32 binaries when built with authorization, pack capability/provenance manifests.

Done: clean-stock and Esteria profile transformations are reproducible and reject unknown/stale images
before writes. Native ABI/exports/catalog limits pass harnesses on exact artifacts. Failure to obtain
stock support blocks R02; an Esteria-only runtime is a development milestone, not the complete module.

## I09 — Transpose full Glue UI and implement branding

- [ ] Status: not started. Requirements: R03–R05, R15. Dependencies: I03, I04, I08.

Copy current effective login/select/create/customize/ECS Lua/XML/TOC and full asset closure. Introduce
generated ID metadata/branding bindings and preserve wrapper order, current scenes, persistence, dialogs,
dropdown preview/cancel/randomization and stock resets. Guard absent optional integrations. Add separate
login/select logo conversion/layout inputs and bundled defaults. Produce UI-only `rebrand` plans without
touching native/server/appearance data. Use locale-aware effective archive resolution.

Outputs: `client/glue/`, `client/branding/`, required addon/adapters, UI generators, branding profile
schema/fixtures, complete shared UI pack and rebrand operation artifacts.

Done: full Glue is installed for every subset; either/both logos change independently without affecting
faction badges/other dialogs. Invalid supplied art fails staging. Current scenes/controls and real-index
selection work on the clean target with only bundled dependencies; named visual acceptance remains required.

## I10 — Install coordinated 100-character support

- [ ] Status: not started. Requirements: R06, R11, R12. Dependencies: I06, I08, I09.

Generate server account/realm defaults 100/100, extend pinned stock validation as needed and preserve
independent heroic limits. Audit create/restore/transfer/dump/optional bot paths. Include guarded client
enum-limit transformation and verify interaction with capacity extension. Preserve full ECS index
binding, scrolling/virtualization/creation controls and persistence through 100. Preflight host policies
and saved counts before changing/reducing caps; never silently hide/delete excess characters.

Outputs: adapter limit hunks, config/update plans, profiled client step, full-roster fixtures,
capacity downgrade policy and receipt fields.

Done: authorized isolated checks demonstrate create/select/login beyond ten, full 100 roster, configured
boundary rejection and account accounting across realms. Client cap >= realm policy; all service actions
use actual indexes. Historical offset checks alone do not satisfy this task's live criteria.

## I11 — Generate deterministic selected/all releases

- [ ] Status: not started. Requirements: R01, R03, R10, R13, R14. Dependencies: I04, I07–I10.

Implement `inspect/plan/stage` CLI and matched generation orchestration. Selection accepts `all`, species
and faction keys and adds shared required UI/capacity/assets. Produce effective mounted archive plans,
loose runtime/catalog/addon outputs and server payload from one lock. Validate archive count/precedence,
profile input freshness and complete closure. Emit complete offline selected/all bundles and an online
pack catalog; no required manual download/copy from the original client is allowed.

Outputs: `tools/racepack/cli.py`, staging generator, `release/{manifest,packs,asset-ledger}.json`,
server/player staging trees, complete offline bundles and content-hash reproducibility report.

Done: single/faction/subset/all plans are deterministic; dependency-only donors stay hidden; shared owners
prevent removal damage. Generated payload closure has zero unresolved reachable references on clean input.
Development artifacts remain clearly distinct until every in-scope race can satisfy `all`.

## I12 — Implement installation, update, recovery and rollback

- [ ] Status: not started. Requirements: R11–R14. Dependency: I11.

Implement server/client install adapters, preflight space/process/mount/DB checks, hash-verified backups,
durable journal and DESIGN phase transitions. Apply file changes by verified temporary replacement,
scoped DB row transactions and explicit DDL actions. Add installed verification, resume, compensating
rollback, rebrand and creation-disable commands. Check receipt state before reverting later modified
files/rows. Preserve existing characters and private before-images. Do not restart unrelated services.

Outputs: `tools/racepack/{install,journal,recover,verify,update}.py`, operator launcher/runtime package,
receipt schema/fixtures, conflict diagnostics and failure-injection integration cases.

Done: clean install/idempotent rerun/upgrade/partial-failure resume/rollback are verified in isolated
fixtures. Stale or foreign changes fail before unsafe replacement; coordinated matched state is restored.
Separate remote server/client operations consume the same release without assuming local co-location.

## I13 — Validate representative end-to-end pilots

- [ ] Status: not started. Requirements: R02–R16. Dependency: I12.

Use High Elf, Gnoll, Earthen, Haranir and Kobold as representatives of legacy, native-five, six-byte,
uint64 and faction-local shared-body contracts. Each pilot includes full Glue, independent logos and
100-character support. Install on an isolated clean client/minimal AC server without development patches
or caches. Run VALIDATION static/native/protocol/install checks and named live scenarios.

Outputs: hashed pilot release/receipts, requirement evidence matrix, live scenario records and defect tasks.

Done: pilots meet their applicable requirements with exact release artifacts; fixes invalidate/repeat
affected checks only. Pilots do not certify other races or satisfy the final `all` requirement.

## I14 — Complete every race and publish-ready release artifacts

- [ ] Status: not started. Requirements: R01–R16. Dependency: I13.

Integrate every reconciled family/repair recipe, preserve existing appearance/gender/class scope and
complete all closure/acceptance cases. Add optional integration profiles only after required standalone
behavior works. Run authorized pinned Windows/Linux server CI and x86 runtime checks plus clean profile
acceptance. Package every mandatory asset/runtime component, docs and complete offline `all` bundle.
Audit provenance and output checksums; stage public metadata without publishing as part of preparation.

Outputs: complete release candidate, compatibility/acceptance matrix, installation/development docs,
artifact catalog, offline bundles, selected release fixtures and upgrade/rollback instructions.

Done: R01–R16 are satisfied for declared supported profiles and every required race. Any incomplete
mandatory identity/profile/asset keeps complete release status failed; experimental artifacts are named
separately. Actual external publication follows the authorization of the implementation task.

## I15 — Migrate Esteria incrementally

- [ ] Status: not started. Requirements: R08, R11, R12, R14. Dependency: I14.

Stage an Esteria migration lock preserving current IDs/frozen codecs, existing characters and unrelated
systems. Identify duplicate old module registrations/mounts/continuations and remove race ownership
only after replacement readiness. Rehearse on a cloned server/client/DB state and verify before-images.
Prepare reviewed source/config/data/client changes and rollback; deploy only when explicitly authorized.

Outputs: private target migration plan/receipts, reviewed removal/replacement diff, backups, rehearsal
report and named post-migration live evidence.

Done: no character appearance/identity regressions or unrelated feature changes; old race ownership is
retired without duplicate scripts or stale overrides. Matched module/runtime/assets are installed and
live accepted; rollback remains viable. Do not label a prepared rehearsal as a deployed migration.
