# mod-esteria-races source extraction and reconciliation instructions

Use with [PLAN](custom-race-module.PLAN.md). Paths in source listings are relative to the Esteria
checkout unless explicitly external. Destination paths are relative to the new module repository.
Do not relocate/delete current working sources or deploy the extracted content during extraction.
Copy frozen inputs, preserve provenance and refactor in the isolated destination.

## Baseline evidence to refresh in I01

- Current tracked and untracked source, manifests, generated headers and related pending SQL.
- Loose active client executable/DLL/catalog/extension files and their import/manifest contracts.
- Effective MPQ/locale/loose precedence and hashes of race DBCs and full Glue/UI/scene files.
- Effective server DBC mounts, continuation order and world SQL overlays, not only repository files.
- Actual compiled worldserver revision/image where discoverable, distinct from dirty working source.
- Read-only target schema, owned startup/racial rows and aggregate saved identity/codec counts.

Preserve [INVENTORY.json](custom-race-module.INVENTORY.json) as the October 14 source snapshot.
Write fresh evidence to an external staging root referenced by `baseline.lock.json`; large payloads stay
outside this planning directory/Git. Do not copy account credentials, WTF/SavedVariables, player notes or
personal character records into published packs. Target-specific migration before-images remain private.

The `Races/` extraction contains `Races.MPQ`, runtime copies, source overlays, DB exports, per-entry
manifests and receipts. Reuse `Races/package_races.py`, `package_support.py`, `resolve_texture_gaps.py`
and `verify_package.py` as recipes after refactoring parameters. Do not run their workstation-specific
capture/deploy behavior unreviewed. `Races/Server/server-since-core-import.patch` is broad context only.
`RaceGuide/sources/` and historical plans help reconstruct provenance, but current working inputs win.

## E01: Identity, eligibility and selected policy

Sources:

- `modules/mod-custom-server/data/races/race_registry.json`.
- `data/retroported-races/allocation.json` and all sibling race manifests.
- `src/server/shared/SharedDefines.h` actual IDs, mask/visual/paired helpers.
- `src/server/game/Entities/Player/RaceMgr.{h,cpp}` derived capacity and masks.
- Effective ChrRaces, SQL overlays, creator metadata and saved character identity counts.

Destination: `data/registry/`, species manifests, generated identity definitions and `src/RacePolicy.*`.
Keep core capacity/helper call-site changes in the adapter. Add explicit actual-ID installed/enabled/
retained sets; do not rely on the current enum/range helpers as a selectable install policy.

Resolve the following before emitting the complete registry:

| Case | Required resolution artifact |
| --- | --- |
| 24–27 client/SQL/registry drift | Per-ID effective and saved meaning; reviewed preservation/migration mapping |
| 29 Kul Tiran, 30/31 Illidari absent from registry/enum | Reconciled legacy policy with complete asset/start roots |
| 61 Alliance Ogre vs remaining Furbolg manifest | Saved-owner evidence; separate collision-free Furbolg identity |
| 15 legacy Sethrak vs active 62 | Preserve legacy non-playable status; explicit active identity mapping |
| 67 Horde Kobold missing registry | Confirm effective/compiled/saved state and add verified policy |
| Vrykul M/F and newer Naga replacing older guide scope | Current manifests/art/receipts and codec identity |
| Kobold two genders sharing one body | Accurate shared-body declaration and faction-local stable choices |
| 32–42 NPC reservations | Non-playable reservation ledger; no automatic inclusion as selectable races |

Reconciliation output `identity-reconciliation.json` contains evidence hashes, old meanings, new stable
keys/IDs, affected saved counts, conflict decisions and unresolved flags. A stage with unresolved flags
cannot generate an `all` release. Never silently reinterpret a character's old race or bytes.

## E02: Core and startup behavior

Audit these sources into a file/hunk matrix; do not copy entire files over arbitrary upstream:

- `src/server/game/Globals/ObjectMgr.{h,cpp}` player-info/stat capacity, startup additions/exclusions.
- `src/server/game/DataStores/DBCStores.{h,cpp}` race-dependent sections/skills and loading.
- `src/server/game/Entities/Player/Player.{h,cpp}` race validation, identity/team/racial paths.
- `src/server/game/Handlers/CharacterHandler.cpp` creation, enumeration, faction/race services and limits.
- `src/server/game/Server/WorldSession.h` creation state and extension parsing.
- `src/server/game/Entities/Player/PlayerStorage.cpp` appearance save/load and live application.
- `src/server/database/Database/Implementation/CharacterDatabase.{h,cpp}` prepared statements.
- `src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp` extension-field replication.
- `src/server/game/World/WorldConfig.cpp`, worldserver dist config and related restore/transfer paths.

Destination: `integration/acore/<pinned-sha>/` checked race-only patch and compatibility manifest.
For each hunk record feature, requirement, stock fallback, hook alternative, dependencies and test.
Exclude MoveCast, Battlemon, progression, unrelated Freeborn/classless/Eluna/playerbot content.
Any inseparable dependency must be refactored or made an explicit optional adapter, not silently carried.

Startup sources: effective table rows and `Races/Server/Database/` exports for playercreateinfo/actions/
items/skills/spells, custom exact-race inclusions/exclusions, race stats/totems and chrraces_dbc.
Destination: owned per-race startup recipes and module shared schema. Broad shared-mask exports are
reference input; derive selected requirements without replacing another host's progression policy.
Generate language/skill/spell admissions together and preserve declared donor/class combinations.

## E03: Racial scripts

- `modules/mod-worgoblin-high-elf/src/Worgoblin.cpp` -> split `src/racials/Broken.*` and `Worgen.*`.
- `src/server/game/Entities/Player/BrokenRacialEffects.h` plus all callers -> owned helpers/needed adapter hooks.
- `modules/mod-custom-server/src/darkfallen_racials.cpp` -> `src/racials/Darkfallen.*`.
- Corresponding world SQL, Spell/visual/icon data and script bindings -> per-race owned data/art roots.
- Audit `mod_race_costumes.cpp` separately; retain race necessities without importing unrelated costume policy.

Update new loader registrations and remove duplicate registration only during a later reviewed Esteria
migration. Preserve Broken IDs/repair/mana/heal behavior, Darkfallen night/ghost logic and Worgen riding
configuration. Document the racial profile of each other race honestly; visual parity is not Retail spells.

## E04: Appearance definitions and runtime

Sources: `src/server/shared/{Highmountain,Earthen,Haranir,Vulpera,Creature}Appearance.h`, current manifest
choice catalogs, Python generators and native consumers. Destination: stable choice data in species
directories and one shared generated header set used by server and client; generators own the bytes.
Retain old codec versions and source-choice migration maps, including Vulpera v2 and faction-local Kobold.

Native sources:

- `client-customization/NativeAppearance.cpp`, `NativeAppearance.def` -> `client/native/appearance/`.
- `HaranirMaterials.inl`, `ClothingMaterials.inl`, `CosmeticWings.inl` -> shared/optional native units.
- `wxl-races-patcher/DarkfallenCharacterSelect.cpp` and build recipe -> `client/native/select/`.
- External `../AzerothPlex/build/wxl-core/extensions/races-64-esteria/MoreRaces.cpp`, manifest and
  required `wxl/PluginApi.h` -> pinned capacity source/vendor input in `client/native/capacity/`.
- `tools/native_appearance_patch.py`, `archive_capacity_patch.py` -> profiled patch engine/steps.
- Native test sources and `build-native.bat`, `build-races.bat`, select build recipes -> portable toolchain configs.

Remove absolute Visual Studio/sibling/developer include paths in destination build recipes. Preserve
fingerprints and client allocation/refcount/lifetime fixes. Extract exact exports/struct sizes/magic,
calling conventions, required image offsets and completed-update/free hook order into `native-abi.json`.
Do not rename DLL imports/catalog files before a matched migration or dual-name compatibility is defined.

Current loose catalogs include shared Appearance/Geometry/Materials, Highmountain/Earthen, Haranir and
textures, Vulpera and textures, Naga/Tuskarr/Vrykul/ThinHuman/Sethrak/Gnoll plus texture banks,
Saberon/Drakonid plus texture and coverage banks, and optional CosmeticWings. Use the inventory for
exact hashes. Some newer families use shared catalogs rather than a separately named species file.

Capture the actual WarcraftXL/loader import graph, selected extension manifests and third-party inputs.
Do not declare every installed DLL required. Decide required capabilities through dependency evidence;
vendor tested required components and retain provenance/licenses, manifests and configuration.

## E05: Race asset/conversion recipes

Use `tools/playable_race_pack.py`, `retroported_race_pack.py`, `expanded_appearance_pack.py` and the
existing portrait/DBC/StormLib services as shared recipe inputs. Source packers to refactor include:

| Family | Current tool/manifests to audit |
| --- | --- |
| Legacy Goblin/Worgen/High Elf/Broken/older imports | playable/retroported packers, module modpaks, Races export |
| Darkfallen | `darkfallen_race_pack.py`, racial module/data, portrait/runtime bridge |
| Mag'har | `retroported_race_pack.py`, `maghar.json`, later race touchups and Orc2 dependency |
| Skyborne | `skyborne_race_pack.py`, visual/expanded packers, frozen native definitions |
| Mechagnome | `mechagnome_race_pack.py`, animation inheritance and eye/beard repairs |
| Highmountain/Earthen/Haranir/Vulpera | Each named race packer plus current repair/codec/catalog recipes |
| Naga/Tuskarr/Vrykul/Forgotten | creature packer, current manifests, female/animation/equipment repairs |
| Ogre/Furbolg | `ogre_furbolg_race_pack.py`, imports and both Ogre/Furbolg manifests; reconcile first |
| Sethrak/Gnoll/Saberon | Named race packers and animation/body/equipment/clothing/coverage repair tools |
| Jinyu/Kobold | Named race packers, prepare/options update/deploy recipes and faction-local choices |
| Arakkoa/Drakonid | Named race packers/deploy recipes; voice/emote or coverage dependencies |

The [tool inventory](custom-race-module.INVENTORY.md) indexes 137 related tools, including repairs.
Use it to build a recipe dependency graph. Do not replay original deployment commands or installed
character GUID migrations. Freeze final converted asset state and transform recipe APIs to accept
explicit input roots, allocation lock, target snapshot and output root with no live side effects.

Each pack contains actual M2/SKIN/ANIM/BLP/etc. bytes, choice/material/geometry coverage and required
portrait/equipment/voice/visual dependencies. Mag'har Orc2 and Arakkoa's Reforged-provided textures must
be self-contained non-stock payloads where absent on the clean baseline. External G:/R:/C: source paths
record provenance only; published packs cannot depend on them.

## E06: Complete Glue, branding, scenes and addons

Capture effective `Interface/GlueXML`, GlueXML.toc, ECS modules and all reachable `Interface/Glues`,
login-screen, fonts, sounds, custom scene model/texture namespaces and supporting dialog art.
Destination: `client/glue/`, default branding and the shared asset pack. Include AccountLogin, select,
create/customize, CharacterInfo, GlueParent/Strings and wrapper order. Keep current behavior with
generated metadata/branding files introduced before consumers.

Audit `tools/character_ui_pack.py`, `creator_portrait_layout.py`, `customization_layout.py`,
`customization_buttons.py`, `customization_label_repair.py`, dropdown/zoom and race touchup recipes.
Use `race_portrait_pack.py`, derived/creature portrait tools for all creator/ECS/in-game namespaces.
Capture latest `tools/login_screen_pack.py` and `tools/login_ui/` scene/loading repairs, including
Midnight/Sirus assets. Old RaceGuide login snapshots alone do not cover current required UI.

Separate login and select logo bindings from any shared `Glues-WoW-WotLKLogo`; preserve other dialogs
and faction emblems. Include bundled defaults and installer-supplied converted replacement bytes.
Loose addon closure is separate from MPQ extraction: audit required TOCs, code/libraries/textures/fonts.
DragonUI adapters and required in-game race portrait/name hooks must be explicit. Cache directories and
SavedVariables are not distributable assets. Optional AIO/Eluna payloads must have an explicit adapter.

## E07: Expanded character capacity

Sources: `docs/100-character-support.md`, `docs/CHARACTER_SELECT*.md`, WorldConfig, creation/restore/
transfer/dump checks, current executable comparison, ECS roster/index/persistence implementation.
Destination: adapter/config policy, guarded executable step, complete roster UI and capacity fixtures.
Retain per-account/per-realm distinctions and defaults 100/100; no implicit Death Knight expansion.
Profile historical offsets/hashes rather than copying a literal patch to unverified binaries.

## Extraction completion artifact

Write `extraction-ledger.json` with source hashes and proposed destination for every owned source/data/
asset, transitive dependencies, exclusion reasons and unresolved items. Code extraction, actual payload
capture, converter recipe capture and live acceptance are separate statuses. All required assets must
be bundled/generated/verified stock; unresolved reachable dependencies fail I04/I11 and the full release.
