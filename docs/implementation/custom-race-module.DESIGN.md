# mod-esteria-races implementation design and contracts

This is the required initial design. Names below are destination contracts to implement, not existing APIs.
Record any necessary revision with rationale and updated requirements/tests before diverging.

## Architecture and ownership

Use C++ for AC scripts/native runtime and Python for portable inspection, generation and installation.
Adapt existing StormLib/DBC/converter tools; do not introduce a second incompatible asset parser.
Package a frozen Python runtime/launcher for operators if Python is not installed. Keep Blender/CASC/
conversion SDKs in developer tooling only. Native DLLs remain Windows x86; server module is portable.

```text
mod-esteria-races/
  CMakeLists.txt
  conf/mod_esteria_races.conf.dist
  src/loader.h, RacePolicy.*, RaceStartup.*, RaceDiagnostics.*
  src/racials/{Broken,Darkfallen,Worgen}.*
  src/generated/                     # checked generated policies/codecs, not hand edited
  data/registry/{species,identities,allocations}.json
  data/races/<species>/{manifest,choices,dbc-deltas,startup}.json
  data/migrations/                   # recipes; selected seeds not auto-scanned unconditionally
  schemas/                          # normative JSON schemas
  integration/acore/<sha>/           # minimal checked patch + compatibility.json
  integration/{playerbots,eluna}/    # optional versioned adapters
  shared/generated/                 # one source of codec/identity definitions for both builds
  client/native/{appearance,capacity,select}/
  client/profiles/12340/<profile>/    # executable guards, ordered patch steps, runtime requirements
  client/glue/                      # complete current Lua/XML/TOC, generated race/brand bindings
  client/branding/default/
  client/addons/
  tools/racepack/                    # inspect/resolve/generate/stage/install/verify/recover services
  tests/{unit,integration,native,protocol}/
  docs/{implementation,compatibility,installation,development}/
  release/                          # generated pack manifests; payloads external to Git
```

Use loader/CMake registration conventions for the pinned AC revision. Current local precedent is
`AC_ADD_SCRIPT`, `AC_ADD_SCRIPT_LOADER` and `AC_ADD_CONFIG_FILE`; these are evidence to adapt, not a
claim about every revision. A module startup diagnostic must reject missing adapter ABI/generated policy
or unresolved declared DBC schema requirements before accepting custom creation.

One lockfile is the source for server identities, native mappings, Glue metadata, DBC/SQL outputs,
catalogs, packs and installer receipts. Different races may share donors, assets and display rows.
Keep a distinct identity set for loaded content, enabled creation and retained existing characters.

## Manifest and artifact schemas

Implement strict versioned schemas in `schemas/`; reject unknown versions and ambiguous field values.
Use paths relative to package roots, POSIX separators in manifests, case-normalized archive lookup keys,
and validated destination paths. Preserve canonical original paths for Windows/MPQ writing. Reject path
traversal, absolute external install paths and duplicate keys. Do not serialize secrets in artifacts.

| Artifact | Required fields and meaning |
| --- | --- |
| `race-manifest.schema.json` | Species, identities, art/codec/startup/UI roots, capabilities, owned keys, acceptance |
| `choices.schema.json` | Stable source ID, label, gender/class rules, default, requirements and action references |
| `selection.schema.json` | Requested species/factions, profile, features, branding inputs, account/realm caps |
| `selection-lock.schema.json` | Fully resolved IDs, digests, pack versions, codec/ABI versions and baseline snapshots |
| `asset-ledger.schema.json` | File/entry, size/hash, owners, ref origins, destination, bundled/generated/stock status |
| `patch-profile.schema.json` | Build/arch, accepted hashes, site guards, ordered transformations, required exports |
| `release.schema.json` | Lock digest, profiles, packs/runtime payloads, installed limits and signatures/hashes |
| `receipt.schema.json` | Operation/release IDs, before/after files/rows, journal, backups and acceptance records |

Identity fields: `key` (stable string), `species_key`, `preferred_race_id`, resolved `race_id`, `faction`,
`file_string`, localized names, `legacy_mask_donor`, `visual_donor`, `paired_identity`, gender/class sets,
start profile and creator ordinal. Actual IDs must never be inferred from names or list position.
Gender support records whether bodies are authored or shared; do not invent female art for male-only races.

Codec fields: `codec_id`, `version`, `transport_tier`, gender-specific ordered descriptors, stable-choice
mapping, default values, cross-choice requirements and explicit exclusions/limitations. Every descriptor
defines stored byte/extension location, radix/count and geometry/material action references. Keep frozen
legacy definitions as versioned inputs, including mappings for existing characters.

Ownership fields identify exact DBC table/key and SQL table/primary-key tuples. Ranges are allocation
constraints, not permission to delete every row in the range. Shared payloads have multiple owners.
Foreign data cannot become module-owned simply by matching a donor race or an ID range.

Hash reproducibility: canonical JSON UTF-8/LF, sorted object keys, stable list order where meaningful,
SHA-256. Keep volatile timestamps/absolute workstation paths outside canonical content digests. A lock
embeds snapshot hashes, not mutable “latest” aliases. Semantic selected content drives generated headers;
branding alone must not invalidate server/native code artifacts.

## Resolution and generation services

`InspectTarget` returns server revision/module ABI/schema/mount/row ownership, client profile/locale/
archive/loader state, existing selected characters and baseline hashes. Direct DB and container access
are adapters; neither is embedded into packer logic. Read credentials from operator configuration or
secret inputs and redact diagnostics/receipts.

`ResolveSelection` expands species/factions and shared dependencies, validates ownership, and produces
the immutable lock. Dependencies requiring a donor's metadata do not automatically enable that donor's
playable button. `all` expands the reconciled ledger, not a manually curated convenient subset.
Esteria migration preserves ID/codec meaning. Fresh targets may remap before characters exist; a later
upgrade uses the prior lock and stable source choices rather than choosing new IDs opportunistically.

`GenerateMatchedSet` performs these independent outputs from the same lock:

1. Server policy/codecs, selected startup recipes, exact-identity enablement and custom racial bindings.
2. Target-effective client and server DBC merges with string-pool rebuild, references and required ordering.
3. Shared/specialized catalogs and texture banks using existing native ABI/version rules.
4. Complete Glue package with selected metadata, independent brand bindings and expanded roster policy.
5. Per-race/shared asset closure, loose runtime/addon files and mounted archive outputs.
6. Reproducible release manifest, per-file ledger and install plan with all target paths.

Preserve unrelated client/server rows and intentional eligibility differences. Serialize writes per MPQ.
Avoid relying on automatic DBC row combination across MPQs. Use one effective shared DBC/UI overlay
and consolidated selected-asset archives to stay within profiled archive-count limits. Payload chunking
for downloads must not dictate the mounted archive count.

## Core adapter contract

Introduce a small versioned core-facing API, named provisionally `CustomRaceBridge`, with default stock
behavior when the module is absent. Its location/linkage must respect the pinned target's build graph:
the core must not directly include module source paths or depend on script-loader initialization for
earlier DBC/character-start initialization. Define registration/availability ordering explicitly.

Required operations: identity membership/creation validation; bounded eligibility/visual donor lookup;
appearance validation/default normalization; exact-race startup contributions; create/enum appearance
transport; load/save/live-field application; race/capacity diagnostics. These are contracts to implement
using audited hooks or narrowly added extension points. Do not assume ordinary PlayerScript callbacks
can replace packet parsing, prepared DB statements or update-field replication.

I06 decides registration order and API signatures after inspecting the selected AC revision. Data needed
before script loading must use generated core-visible definitions or a correctly scheduled early hook.
The adapter must be race-only: capacity/index arrays, safe mask consumers, ObjectMgr initialization,
DBC loading, creation/enum/storage/update integration, and character-cap validation/related paths.
Shared generated definitions remove race-ID switches from both runtimes where feasible. If a selected
mapping remains compiled, record that changing it requires rebuilt matched artifacts.

Module runtime config may narrow creation to identities contained in the release, never enable absent
content. Check actual RaceID on character creation/service paths. Keep stock races working and preserve
existing-character login for creation-disabled identities. Do not globally widen legacy eligibility masks.

## Appearance ABI to preserve

All native catalog parsing is little-endian with bounded magic/version/count/path/payload checks.
Reuse EAPP v2, EAGM v1, EAMT v1 and specialized EHM1/EHT1 readers; coverage formats are separately
defined by current source. Exact layouts must be extracted, documented and checked in I03/I08.

| Tier | Create | Enum | Persistent/live state |
| --- | --- | --- | --- |
| Stock five | Skin/face/hairStyle/hairColor/facialStyle | Existing bytes | Existing fields, frozen radix semantics |
| Six-byte | Extra value in unused outfit byte | HXE1 GUID/byte pairs | extraAppearance, Unit padding |
| Five+uint64 | uint64 + HRC1 trailer | HXE2 GUID/uint64 pairs | BIGINT extraAppearance; low Unit/high Object words |

Preserve HRC1 `0x31435248`, HXE1 `0x31455848`, HXE2 `0x32455848`; document exact current count,
ordering and trailer peeling in fixtures. Reject invalid signatures/lengths/choices/genders/classes.
The client removes trailers before stock enum parsing. Mixed rosters and optional CWG1 must not lose
another trailer's records. Current image/helper lifecycle/calling-convention repairs remain required.
Declare padding ownership; foreign conflicts must be diagnosed before install.

First release requires the matched patched client for extended appearance; arbitrary-client negotiation
is not assumed. Publish that requirement and diagnose configured incompatibility before deployment.
Any future runtime capability handshake must be a separately specified protocol extension.

## Glue, branding and character limits

Transplant current effective Lua/XML/TOC and every shared UI/scene dependency, not only old snapshots.
Generate `EsteriaRaceMetadata.lua` and `EsteriaBranding.lua` before their consumers in the new TOC.
These proposed files centralize actual-ID mappings and independent login/select asset paths/layout.
Keep ECS wrapper order and real-index action binding. Optional Freeborn/name/cosmetic code is guarded.

Branding namespace: `Interface/Glues/EsteriaRaces/Branding/{LoginLogo,CharacterSelectLogo}`.
Convert default/replacement artwork through the existing supported BLP/TGA pipeline. Missing supplied
artwork fails staging; absent overrides use bundled Esteria defaults. Preserve fades and anchor behavior.
Images are bundled bytes, not references to an operator's absolute paths. UI-only rebranding does not
rewrite DBCs, character fields, executable or native DLL.

Generate account=100/realm=100 defaults and the server effective-config update plan. Preserve independent
Death Knight settings. The initial portable limits remain 1–100 with account >= realm; diagnose a host's
larger/incompatible policy rather than automatically reducing it. Create >10 support includes a guarded
client enum-limit patch, native roster consistency and full ECS reachability/persistence at 100.
Historical `0x6404F` and VA `0x00464C4F` are profile evidence, never universal patch offsets.

## Installer commands and state machine

Implement CLI entry point `racepack` with `inspect`, `plan`, `stage`, `install-server`, `install-client`,
`verify`, `update`, `rebrand`, `disable-creation`, `recover` and `rollback`. Commands emit compact human
status plus JSON artifacts. Read-only `inspect/plan` and offline `stage` must not write live paths.
`install-server` and `install-client` consume the same release; neither assumes both targets are local.
Stage verifies available space including backups and checks that all pack hashes/versions resolve.

Journal phases: `planned -> staged -> backed_up -> server_files -> schema -> selected_rows -> server_dbc
-> client_files -> installed_verified -> live_pending -> accepted`. In a client-only operation mark
server phases not applicable, not successful. Record each action before mutation and its verified result
afterward; fsync or use durable platform equivalents before phase advancement.

DB/filesystem changes are not one transaction. Use scoped row transactions, explicit DDL tracking and
compensating restore. A rollback checks current files/rows against installed hashes/version predicates,
then restores matching before-images; foreign later changes produce conflicts rather than being erased.
Resume verifies already completed phases and restores or continues only from the journaled version.
Backups/journals must not reside in mounted Data. Closed WoW/archive editors and coordinated maintenance
are preconditions for application, while generation remains reviewable without service mutation.

Shared version/schema SQL can use the pinned module updater conventions. Optional race seeds belong
to selected-data execution, not unconditional auto-scan. Track ownership and version receipts; never
rerun GUID-specific migrations or import full characters schema snapshots. Existing appearance changes
use GUID-scoped old/new-codec migrations generated for that target only.

## Release artifacts

Publish code/core profiles, matched x86 binaries, per-race asset packs, shared Glue/runtime pack, pack
catalog/ledgers, generated server payload, player installer and offline selected/all bundles. Each
release declares core/client/native/catalog/codec/data ABI tuple and supported profile evidence.
Payload files include actual bytes with SHA-256 and provenance. `all` must remain blocked if a mandatory
family/profile cannot be included; an experimental pilot is a separately named development artifact.
