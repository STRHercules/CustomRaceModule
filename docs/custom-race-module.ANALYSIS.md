# Esteria custom races: inventory and standalone AzerothCore module design

**Implementation status:** this document is supporting analysis. The normative, dependency-ordered
implementation documents are linked in [INDEX](custom-race-module.INDEX.md); start there to create the module.

**Draft date:** October 14, 2026. **Proposed repository:** `mod-esteria-races`.
**Purpose:** extract all race functionality into a dedicated distribution that installs all races or a
selected subset, including server integration, client assets, executable patches, DLLs, catalogs and UI.
The distribution also installs the current Esteria login, character-select, character-create and
customization Glue UI, supports independently replaceable login/select logos, and installs coordinated
server/client support for more than ten characters. The initial target is Esteria's 100-character policy.
The released distribution must supply and install every required non-stock asset for the selected races
and the complete shared interface. Asset completeness is a release requirement, not a later operator task.

## 1. Recommendation and feasibility

Create one dedicated module repository with three coordinated deliverables:

1. An AzerothCore server module containing race policy, startup data, racial scripts and generated codecs.
2. A versioned, minimal core compatibility patch for functionality that ordinary module hooks cannot provide.
3. A client installer/package generator with the full Esteria Glue UI, configurable branding, expanded
   character roster and the required runtime/assets for the race selection.

The existing work cannot become a portable, complete solution simply by moving it into `modules/`.
It changes core race handling, native client tables, appearance packets, persistent character data and
rendering. A compiled server module also cannot directly install files on remote players' computers.
The operator prepares a matched server/client release; each player runs the client installer locally.

“Any AzerothCore server and 3.3.5 client” should mean a broad, explicit compatibility contract:

- Supported AzerothCore revisions and forks, with adapters or a checked core patch where necessary.
- Windows x86 WoW **3.3.5a build 12340** client images with verified executable profiles.
- A clean client and supported modified clients, preserving unrelated target modifications.
- Locale-aware asset/UI installation, starting with enUS and expanding only after validation.
- Linux/Windows server support; Wine client support only after a separate validation matrix.

An arbitrary modified executable or fork cannot be promised compatible in advance. Unknown binaries,
conflicting IDs, incompatible packet extensions and foreign UI replacements need a diagnostic and an
explicit merge/adaptation path. Retain fingerprint guards; removing them does not establish portability.

The Esteria Glue interface and expanded character capacity are required deliverables for this module,
including installations selecting only a few races. Logo replacement changes the operator's branding
without requiring a fork of the interface or affecting which races are installed.

The installer must work from a supported clean 3.3.5a client and normal AzerothCore base data plus the
module's release payloads. It must not depend on Esteria's existing client, donor patches, workstation
directories or separately hand-copied artwork. Required shared assets install even for a single-race subset.

## 2. Evidence, scope and where the complete inventory lives

This draft uses current working files at HEAD `a6f7e6d0a36b8f5bb6900a6cd79850ccb2c45bdb`, including
uncommitted race work. It also reads the loose files in `G:\3.3.5a - Dev`, the sibling WarcraftXL source,
the `Races/` export and the earlier `RaceGuide/`. No build, test suite, SQL import, service restart,
executable edit or live character interaction was performed for this draft.

- [INVENTORY.md](custom-race-module.INVENTORY.md): every inspected loose runtime file, size, SHA-256,
  export comparison, current race manifests, 137 related Python tools and installed addon directories.
- [INVENTORY.json](custom-race-module.INVENTORY.json): exact allocations, registry, manifest models and
  external source paths, current source hashes, addon TOC hashes and export receipt metadata.
- [Capture script](custom-race-module.capture.py): repeatable read-only inventory of these inputs.
- [Races README](../../../Races/README.md), [server export README](../../../Races/Server/README.md),
  [MPQ manifest](../../../Races/mpq-manifest.json) and
  [support manifest](../../../Races/support-manifest.json): existing payload ownership/provenance evidence.
- [RaceGuide](../../../RaceGuide/README.md): detailed historical recipes and named live acceptance records.

The existing export receipt records **56,811 MPQ entries**, **1,083 support files**, **40 custom race
slots**, and a 3,343,080,721-byte MPQ on October 9. These are historical capture counts, not today's
complete race count. Current loose-file comparison finds three changed shared runtime files:
`EsteriaAppearance.dll`, `EsteriaAppearance.bin` and `EsteriaAppearanceGeometry.bin`.
The three Drakonid catalogs are absent from that export. Four additional root DLLs are also absent;
their presence does not establish a race dependency. Thus the export is a strong extraction starting
point, but cannot be shipped as today's complete matched release without refreshing and reconciling it.

This draft is a dependency and implementation specification, not a fresh certification of every live
DB row or MPQ entry. The installer implementation must freshly resolve effective archives, server mounts,
SQL overlays and character state. Historical source snapshots are evidence, not the current build input.

## 3. Race inventory and reconciliation

Keep a species distinct from its faction-specific playable identities. Some species share models but
use separate RaceIDs, languages, starts and donor masks. Slot count is not species count.

| Current IDs | Family / identity | Current evidence and packaging requirement |
| --- | --- | --- |
| 1–8, 10–11 | Original ten Wrath races | Preserve; additive Ascension appearance expansion is a selectable feature |
| 9 | Goblin, Horde | Worgoblin runtime/start/racial data plus player assets |
| 12 | Worgen, Alliance | Worgoblin; include Running Wild and its configured riding behavior |
| 13 | High Elf, Alliance | Blood Elf-derived visuals, own identity/start/language policy |
| 14 | Broken, Horde | Bespoke player assets and implemented Broken racials |
| 15 | Legacy Sethrak, Horde | Export flags it non-playable; do not silently activate alongside 62 |
| 16–23 | Imported families (listed below) | Vulpera 20 has a Retail rebase and frozen v2 codec |
| 24–27 | Broken/Forsaken/Pandaren variants | Historical client/registry/SQL identity drift; reconcile |
| 28 | Dracthyr, Horde | Imported player graph; does not imply a complete dragon-form gameplay system |
| 29 | Kul Tiran, Alliance | Present in export, absent from current registry and race enum; reconcile |
| 30/31 | Illidari, Horde/Alliance | Present in export, absent from current registry and race enum; reconcile |
| 32–42 | Reserved NPC identities | Preserve reservation/NOT_PLAYABLE policy; exclude from selectable playable packs |
| 43/44 | Darkfallen, Alliance/Horde | Shared models, separate faction identity and implemented racials |
| 45 | Mag'har Orc, Horde | Final graph uses working Orc2 geometry and baked Mag'har textures |
| 46 | Highmountain Tauren, Horde | Expanded controls, BONE face work, six-byte appearance |
| 47 | Mechagnome, Alliance | Mechanical collections, parent animation inheritance, five-byte appearance |
| 48/49 | Earthen, Alliance/Horde | Expanded controls and six-byte persistence |
| 50/51 | Haranir, Alliance/Horde | 29/28 changing controls; five-byte plus uint64 persistence |
| 52/53 | High Order/Windshaper Skyborne | Expanded controls packed into five bytes; Forever-derived assets |
| 54 | Naga, Horde | Current manifest is later Sirus-based M/F graph; older six-skin guide is superseded |
| 55 | Tuskarr, Alliance | Male-only authored model; equipment/feet/robe rules |
| 56/57 | Vrykul, Alliance/Horde | Current manifest/allocation includes female work; older male-only guide is stale |
| 58/59 | Forgotten, Alliance/Horde | Technical asset/catalog namespace remains ThinHuman; male-only policy |
| 60/61 | Ogre, Horde/Alliance | Current enum/registry/allocation make 61 Alliance Ogre; shared M/F model graph |
| historical 61 | Furbolg | Remaining `furbolg.json` also claims 61; cannot coexist there with Alliance Ogre |
| 62 | Active Sethrak, Alliance | New animated/player integration; current manifest supports M/F |
| 63 | Gnoll, Horde | Male-only; native clothing/material, armor/cloak and player-component repairs |
| 64 | Saberon, Horde | Male-only; equipment fitting and texture coverage catalogs |
| 65 | Jinyu, Alliance | Supplied player graph, M/F, River Jinyu/Ankoan body options |
| 66/67 | Kobold, Alliance/Horde | Both declared genders share the supplied female model; 67 missing from registry |
| 68 | Arakkoa, Horde | M/F supplied pack rebased from donor race 45; voices/emotes/custom spells |
| 69/70 | Drakonid, Alliance/Horde | Male-only modern creature port, shared art, texture coverage and equipment work |

IDs 16–23 are Eredar, Nightborne, Alliance Pandaren, Void Elf, Vulpera, Lightforged Draenei, Zandalari Troll
and Dark Iron Dwarf, respectively. Policy IDs 24–27 are Alliance Broken, Forsaken, Horde Pandaren and
Horde Broken, respectively.

All these families belong in the extraction audit. Do not discard legacy variants merely because the
newer JSON registry omits them. Conversely, a manifest or enum is not evidence of a fully installed,
playable, accepted package. Furbolg needs a new collision-free allocation if it is to be retained as a
separate selectable race. Reserve its new identity only after target audit; do not reinterpret existing
race-61 characters. Kobold's shared body must be described accurately rather than advertised as two
different authored gender models.

The current registry has 55 playable policy rows, including the ten stock races; it is not a complete
authority by itself. Resolve disagreements using saved characters, effective ChrRaces/UI, SQL overlays,
allocation history and receipts. Create a reconciled ledger before generating the first module release.

## 4. How the current system works

### 4.1 Identity, capacity and eligibility

The authoritative tuple includes actual RaceID, species key, faction, visible/localized name, file string,
creator ordinal, model/display IDs, gender policy, class policy, starting profile, equipment prefix,
visual donor and eligibility donor. None of these can substitute for another.

`src/server/shared/SharedDefines.h` defines custom IDs and helpers such as `GetRaceMaskForRace`,
`GetLegacyMaskRaceForRace`, `GetVisualBaseRaceForRace` and `GetPairedRaceForRace`.
`src/server/game/Entities/Player/RaceMgr.cpp` derives server capacity/mask sets from playable loaded
ChrRaces rows. It does not read `race_registry.json` itself; the JSON is policy/generation input.
`ObjectMgr` uses dynamic player-info/stat arrays and custom startup inclusion/exclusion support.

The client extension still named `races-64-esteria.dll` now supports **129 slots, IDs 0 through 128**.
Its live manifest says 2.0.0; current `MoreRaces.cpp` has `kRaceCount = 129`. It extends both-gender model
tables, name fallbacks, initialization, cleanup and race restrictions. The imm32 comparison avoids the
signed immediate problem at 128. `NativeAppearance.cpp` also uses 129 races and 258 race/gender profiles.
Glue button capacity is separate from numeric identity; Vulpera creator ordinal 17 is RaceID 20.

Legacy eligibility remains **32-bit**, with safe donor aliases for high IDs. Examples: Mag'har→Orc,
Highmountain→Tauren, Mechagnome→Gnome, Earthen→Dwarf/Orc, Haranir→Night Elf/Troll, Skyborne→High Elf/
Blood Elf, Naga→Blood Elf and newer Horde creature ports→Orc. Darkfallen uses `0x80000000`.
Always use bounded mapping; `1 << (race - 1)` is invalid for high IDs. Donor masks can grant shared
eligibility but cannot uniquely select a race, faction, install set or custom racial.

For selectable installation, add explicit numeric identity membership checks. The present range helper
`IsExtendedPlayableRace` and donor masks are insufficient to reject a disabled race sharing an enabled
race's donor. Preserve login for retained existing characters when only new creation is disabled.

### 4.2 Server data, initialization and racial mechanics

Race starts are more than `playercreateinfo`. The existing server export includes:

| Data | Required meaning |
| --- | --- |
| `chrraces_dbc` / full ChrRaces | Identity, flags, model displays, faction/language/cinematic metadata |
| `playercreateinfo` | Per-race/class start map, zone, coordinates/orientation |
| `playercreateinfo_action` | Initial action bars |
| `playercreateinfo_item` / CharStartOutfit | Startup items and client preview outfits |
| `playercreateinfo_skills` | Shared donor-mask skills and class eligibility |
| `playercreateinfo_spell_custom` | Shared start spells, including existing host policy |
| `custom_race_start_skill` and `_exclude` | Actual-race skill additions/exclusions |
| `custom_race_start_spell` and `_exclude` | Actual-race spell additions/exclusions |
| `player_race_stats` | Race stat modifiers |
| `player_totem_model` | Shaman totem model policy |
| Spell/script bindings and related DBCs | Implemented racials and their client presentation |

Languages require matching skill and spell initialization, server SkillRaceClassInfo admission,
SkillLineAbility policy and client eligibility redirects. Skill step zero is significant in established
repairs. Confirm chat after relog; a stored row or tooltip is not sufficient.

The current broad ten-class policy is `[1,2,3,4,5,6,7,8,9,11]`. Make it an explicit per-race policy and
offer a profile retaining Esteria combinations. Do not import classless progression just to obtain start
spells, or assume native forms/pets/proficiencies work for every race/class pairing.

Broken racial implementation crosses `modules/mod-worgoblin-high-elf/src/Worgoblin.cpp`,
`src/server/game/Entities/Player/BrokenRacialEffects.h` and spell/core call sites. Preserve Salvager,
Krokul's Cunning, Fel-Scarred and Echo of the Naaru with their data/bindings and intended repair/mana/heal
behavior. Darkfallen implementation is in `modules/mod-custom-server/src/darkfallen_racials.cpp`;
extract it with its spell IDs, triggers and startup data. Worgen Running Wild also has module logic.
Newer visual ports frequently inherit donor racials; their names do not imply full Retail mechanics.

Arakkoa adds sound/emote/spell allocations as well as models. Its original donor ID 45 collides with
Mag'har and was rebased to 68. Include voices, referenced spell effects and all related table rows;
verify the complete graph rather than treating five custom spell IDs as the complete dependency list.

### 4.3 Appearance encoding and persistence

Stock transport order is `skin, face, hairStyle, hairColor, facialStyle`. Independent UI controls use
mixed-radix packing: `value = i0 + n0*i1 + n0*n1*i2`; a byte's total capacity must not exceed 256.
Choice indexes encode the value; stable source choice IDs identify choices across migrations.

| Storage tier | Families | Contract to extract |
| --- | --- | --- |
| Five stock bytes | Skyborne, Mechagnome, Vulpera, most creatures | Stock transport; native decoding/validation |
| Five plus one byte | Highmountain, Earthen | Outfit byte; extraAppearance; HXE1; Unit padding |
| Five plus uint64 | Haranir | HRC1; HXE2; BIGINT extraAppearance; low/high live words |

Current generated headers are `HighmountainAppearance.h`, `EarthenAppearance.h`, `HaranirAppearance.h`,
`VulperaAppearance.h` and `CreatureAppearance.h` under `src/server/shared/`.
The server consumers include `CharacterHandler.cpp`, `WorldSession.h`, `PlayerStorage.cpp`,
`CharacterDatabase.cpp` and `UpdateFieldFlags.cpp`. Trace create, save, load, enum, nearby updates,
barber and faction/race change together.

Highmountain/Earthen use the existing unused outfit byte without lengthening stock creation packets.
HXE1 carries GUID/extra-byte pairs followed by count/magic `0x31455848`. Haranir creation appends uint64
and HRC1 `0x31435248`; HXE2 carries GUID/uint64 pairs with magic `0x32455848`. The native reader strips
extensions before stock roster parsing. `extraAppearance` is `BIGINT UNSIGNED NOT NULL DEFAULT 0`.
Live Haranir transport uses low Unit/high Object padding words. Mixed rosters retain both trailer types.

These fields can conflict with other modules using padding or extended packets. Declare ownership and
ABI compatibility, bound parsing, and validate malformed/truncated/duplicate-GUID cases. A vanilla
client must not receive a protocol it cannot consume. The first portable release should require the
matched patched client; a negotiated fallback is a separate implementation, not an assumed capability.

Freeze codecs from the installed manifests. Reordering a choice can reinterpret saved bytes. Migrations
must decode old codec→stable source choice→new codec and record affected characters and rollback data.
Never distribute GUID-specific Esteria migration records to another server. Haranir's eleven used
bytes fit its thirteen-byte contract; preserve its exact allocation. Independent expanded barber
controls are not currently implemented: the existing barber uses legacy combined values.

### 4.4 Native executable and DLL integration

| Component | Current role / location | Extraction requirement |
| --- | --- | --- |
| `Wow.exe` | Customized foundation and redirects | Generate guarded transformations; retain repairs |
| `WarcraftXL.dll` + loader | Extensions and modern capabilities | Audit imports, ABI and conflicts |
| `races-64-esteria.dll` | 129-slot tables | Vendor source/manifest/headers; retain guards |
| `z-darkfallen-character-select.dll` | Roster/model/name bridge | Use manifest entry; exclude stale duplicate |
| `EsteriaAppearance.dll` | Direct executable import | Match exports, headers and catalogs |
| Modern M2 / extended DBC | Model/table compatibility | Include selected dependencies |

Both extension DLLs reside under `Extensions/<extension-folder>/`; the character-select folder is
`z-darkfallen-character-select`. `EsteriaAppearance.dll` stays in the client root.

`tools/native_appearance_patch.py` accepts an exact SHA-256
`2cf5a5cbaa8b27c7497d181a5d08fce2861bb55d66bd12a8b4a2657a67e0c409`, checks
`ESTERIA_CLIENT_FOUNDATION_V3`, validates instructions and adds `.eapp` imports/redirects. That hash
is its expected input, not a claim that today's active executable has that hash.
It redirects geometry/index/draw handling, skill eligibility, creation/enum/live appearance and
component cleanup, and integrates the native customization callback under existing Lua validation.
`tools/archive_capacity_patch.py` supplies a later guarded archive-slot repair. Archive capacity,
race capacity, roster size and character limits are separate mechanisms.

The original foundation injector was not found by the earlier handoff. Current sibling capacity source
is available under `../AzerothPlex/build/wxl-core/`, but source availability there does not prove a
reproducible clean-client foundation transformation. Recover/document that transformation, or build a
separate tested stock-12340 backend, before claiming clean-client support.

The current source/runtime is Win32/x86. Build scripts hard-code a local Visual Studio installation
and sibling source path; replace those with explicit toolchain discovery and vendored/pinned inputs.
The native helper directly imports no WXL customization API, but the selected modern assets and race
capacity still depend on other WXL capabilities. Treat those as distinct dependencies.

Required stability rules from prior fixes:

- Read x86 bool returns from AL; preserve fallback setters.
- Use the verified stdcall client allocator for client-freed image buffers and retain material references.
- Read extension state after completed object updates; reject non-unit objects before Unit access.
- Do not register unsupported padding old-value observers; clear component caches before free/address reuse.
- Native creator offsets differ from packet order; bind descriptors to validated image offsets.
- Preserve guarded model teardown, wide SKIN/index handling and sorted CharSections repairs.

The `Races/ClientRuntime` export also carries `Client.dll`, `dinput8.dll`, `ijl15.dll`, `msvcr80.dll`,
`dbghelp.dll`, `DivxDecoder.dll`, `unicows.dll` and `Battle.net.dll`. It includes extensions
`wxl-awesome-wotlk`, `wxl-extended-dbc`, `wxl-glue-zoom`, `wxl-modern-m2` and
`wxl-no-transparent-characters`. This is a captured support set, not a proved minimal dependency list.
Audit PE imports, dynamic loads, extension manifests and selected payload formats. Package required
components with provenance; make presentation extras optional. Detect existing `dinput8.dll`/proxy
ownership instead of overwriting another loader. Do not turn fog, chat, housing or unrelated Plex
features into mandatory dependencies merely because they are installed on Esteria.

### 4.5 Every current appearance catalog family

These files stay loose in the client root. They are not MPQs or server DB tables.

| Files | Role / selection |
| --- | --- |
| `EsteriaAppearance.bin` | Shared EAPP v2 race/gender option descriptors |
| `EsteriaAppearanceGeometry.bin` | Shared EAGM v1 prepared SKIN data and paths |
| `EsteriaAppearanceMaterials.bin` | Shared EAMT v1 material selections |
| `EsteriaHighmountain.bin` | Specialized Highmountain selectors/material/geometry |
| `EsteriaEarthen.bin` | Specialized Earthen selectors/material/geometry |
| `EsteriaHaranir.bin`, `EsteriaHaranirTextures.bin` | Haranir selections and compressed texture banks |
| `EsteriaVulpera.bin`, `EsteriaVulperaTextures.bin` | V2 cosmetics, layers, eyes and equipment |
| `EsteriaNaga.bin`, `EsteriaNagaTextures.bin` | Current Naga rendering selections/textures |
| `EsteriaTuskarr.bin`, `EsteriaTuskarrTextures.bin` | Tuskarr body/equipment selections/textures |
| `EsteriaVrykul.bin`, `EsteriaVrykulTextures.bin` | Current Vrykul M/F selections/textures |
| `EsteriaThinHuman.bin`, `EsteriaThinHumanTextures.bin` | Forgotten, retaining its technical namespace |
| `EsteriaSethrak.bin`, `EsteriaSethrakTextures.bin` | Active Sethrak rendering |
| `EsteriaGnoll.bin`, `EsteriaGnollTextures.bin` | Gnoll rendering and clothing/material repair support |
| `EsteriaSaberon.bin`, `EsteriaSaberonTextures.bin`, `EsteriaSaberonCoverage.bin` | Appearance/equipment |
| `EsteriaDrakonid.bin`, `EsteriaDrakonidTextures.bin`, `EsteriaDrakonidCoverage.bin` | Appearance/equipment |
| `EsteriaCosmeticWings.bin` | Optional roster cosmetics integration, not a prerequisite for race creation |

Specialized selection formats include EHM1 v1; compressed RGBA banks use EHT1 v1. Coverage catalogs
have separate native readers; preserve their exact version/layout from source. EAPP's 16-descriptor
limit does not cap Haranir's specialized controls. Do not reuse old record counts or infer an empty bank
is missing without parsing its format. Ogre, Jinyu, Kobold and Arakkoa do not each require a newly named
catalog merely because they are separate races; current shared/native paths can cover them.

`HaranirMaterials.inl` provides shared texture-bank/compositor behavior; `ClothingMaterials.inl` and
coverage readers cover newer equipment work. Cache files below `Interface/AddOns/EsteriaAppearanceCache`
are generated outputs, not the persistent character appearance database. The module should regenerate
them locally and should not distribute another player's cache or SavedVariables.

### 4.6 Assets and DBC dependency graph

Each selected race requires the reachable asset closure: M2, all required SKIN/ANIM files, textures,
inherited skeleton tracks, collection meshes, BONE-derived baked geometry where implemented, equipment
variants, portraits, sounds, backgrounds and racial visual effects. Normal stock dependencies remain
in the target client's base archives; non-stock dependencies must be supplied explicitly.

#### 4.6.1 Complete asset packaging contract

“Includes all assets” means the release contains the actual installable payload bytes, not only source
paths, manifests, conversion recipes or links to another server's patch. Versioned downloadable packs
are part of the module distribution and must be resolved automatically by its installer. Provide an
offline bundle containing all packs needed by its declared selection; the all-races bundle contains
all required race packs and shared assets. Large payloads can remain outside Git without being omitted
from the release. A missing required payload blocks packaging and installation before live changes.

| Asset family | Required contents when referenced by installed functionality |
| --- | --- |
| Characters | Body/head models, SKINs, external ANIMs, inherited tracks and converted collection geometry |
| Appearance | Skin/face/hair/eye/accessory textures, atlases/palettes, geosets and baked morph variants |
| Equipment | Race/gender helmet and armor variants, cloak/boot/robe support and attachment dependencies |
| Portraits | Creator, ECS/select and in-game portrait artwork, masks/rings and lookup bindings |
| Glue/interface | All Lua/XML/TOC, fonts, buttons, borders, dropdown/dice/rotation art and dialog dependencies |
| Branding | Default Esteria login/select logos and any operator-supplied converted replacement images |
| Scenes | Login/select/create backgrounds, models/textures/animations, lighting/effects and sounds |
| Gameplay | Required racial spell visuals, sounds/emotes, forms, mounts and totem assets |
| Native runtime | Required DLLs/loaders/manifests/configs, loose catalogs, texture banks and coverage data |
| Addons | Required selected addon code, TOCs, libraries, artwork/fonts and other declared dependencies |
| Server data | Required generated DBCs, scoped SQL, codecs and map/vmap/mmap outputs for selected zones |

Include WMO/ADT/map textures and other scene/map formats where the installed scenes or optional start
zones reference them. Include every animation variant/LOD/texture permutation needed by supported
choices and equipment rules; one working default model or portrait does not establish completeness.
Runtime-generated caches may be regenerated locally, but their required source banks, loader code and
default assets must be included. Do not substitute another race's body or drop authored choices merely
to avoid packaging dependencies.

Build a dependency ledger for each final asset: destination path or archive entry, size/hash, source
provenance, owning race/shared feature, reference origins, required runtime capability and destination
type. Resolve recursively from selected race/DBC roots, native catalogs, addon TOCs and the entire
installed Glue interface. Follow embedded model references, relative paths, inherited animation files,
DBC sound/visual chains and dynamically constructed Lua/native filenames. Static string scanning alone
cannot prove the complete graph; enumerate generated race/gender/choice/locale/equipment paths too.

Full Glue installation may reference artwork or scenes independent of selected race buttons. Keep all
assets reachable from that shared interface, even if they originated in an unselected race pack. Shared
resource ownership must prevent subset installation/removal from deleting those dependencies. Prune
only records/assets proven unreachable from the resolved release, with that decision recorded.

Every final dependency must be classified as **bundled**, **generated from bundled inputs**, or
**provided by the verified stock baseline**. Stock-baseline dependencies must resolve in the supported
clean client's actual base archives or normal server base data. A file found only in Reforged/Sirus/
Ascension/custom patches is a non-stock dependency and must be included in our distribution. Donor
archives and historical development paths are acquisition evidence, not installation prerequisites.

Validate packaging on an isolated clean baseline with only the produced module/client bundle installed,
without mounting the development client's extra patches, loose files or appearance caches. Reopen every
generated archive and verify installed entries/hashes through effective root/locale precedence. Exercise
all supported appearance choices, portraits, equipment rules and Glue scenes/transitions so dynamic
dependencies are tested too. The release asset report must show zero unresolved reachable dependencies;
documented unreachable legacy references do not excuse a missing file used by installed functionality.

Primary tables are ChrRaces, CreatureModelData, CreatureDisplayInfo, CreatureDisplayInfoExtra,
CharSections, CharHairGeosets, CharacterFacialHairStyles, CharHairTextures, CharBaseInfo, CharStartOutfit,
BarberShopStyle, SkillRaceClassInfo, SkillLineAbility, NameGen, Spell and supporting sound/visual tables.
The installer must discover actual usage; not every table needs a change for every race.

Current server full DBC outputs live in `modules/mod-custom-server/data/dbc/retroported-races`;
SkillRaceClassInfo has a separate path. Compose bind mounts and SQL `*_dbc` overlays determine effective
server data. `mod-wxl-dbc` supplies continuation loading and core after-load integration; obsolete
race continuations must not overwrite newer full tables. Freeborn FactionTemplate continuation is separate.

Only the winning copy of a DBC is loaded; multiple race MPQs do not merge table rows automatically.
Generate full target-effective tables from baseline plus selected row deltas, preserve foreign rows,
rebase string offsets and detect collisions. Sort client CharSections by race, sex, section, variation,
color to maintain contiguous cache groups. The prior sort repair eliminated reproduced buffer overruns.
Server and client tables may intentionally differ, especially SkillRaceClassInfo; compare semantics.
Keep player display IDs below 65536 under the accepted PlayerInfo contract; model row IDs are distinct.

A clean client exposes hidden dependencies: Mag'har currently resolves Orc2 geometry, Arakkoa relies on
26 Outland textures provided by Reforged `patch-V.MPQ`, and legacy Kul Tiran uses unusual Naga_ paths.
Include those exact non-stock dependencies in the race pack; do not require the entire Reforged patch.

The export documents 180 unresolved CharSections texture references, 329 unique absent model texture
names and two unparsable helmet texture tables. Those figures are historical audit findings, not a
fresh count. Classify each as reachable defect, native-superseded reference or unused legacy variant.
Block release of a selected race for missing reachable dependencies; retain a report for harmless
unreachable records. Extraction byte verification does not establish visual correctness.

### 4.7 Glue UI, portraits, addons and optional systems

Creation/select/login code is pre-login `Interface/GlueXML`, not an ordinary addon. Include or adapt
CharacterCreate.lua/xml, CharacterInfo.lua, GlueParent.lua, GlueStrings.lua, CharacterSelect and the
required TOC entries. The expanded creator implements labels, dependent choices, defaults, preview/
cancel/commit, randomization and stock-race resets. Current UI generators include `character_ui_pack`,
`creator_portrait_layout`, `customization_layout`, `customization_buttons`, `customization_label_repair`
and race-specific packers. Generate creator entries from the selection, not fixed ordinal assumptions.

Portraits use separate creator, ECS and in-game character-frame namespaces. Include faction/gender
images, ring/mask treatment, BLP encoding and numeric/file-string mappings. Shared visible names cannot
identify faction. Preserve stable asset keys for Forgotten/ThinHuman and all same-name faction variants.

Esteria Character Select (ECS) adds filtering, reorder, notes, virtualization and portrait/schema modules.
Its real character index must survive search/reorder: enter/delete must never use visible row position.
Glue persistence uses bounded CVars rather than addon SavedVariables. The pure ECS files and integration
wrapper require their existing TOC order; preserve compatibility with optional Freeborn wrappers.

Transpose and install the complete current Esteria login, character-select, character-create and
customization interface as the module's standard Glue package. This includes its Lua, XML, TOC ordering,
ECS modules, expanded controls, fonts, textures, portraits, dialogs, backgrounds/scenes and reachable
model/animation/sound dependencies. Include AccountLogin.lua/xml and the login scene selection/loading
helpers as well as the create/select files. Preserve preview, Apply, Cancel and saved-scene behavior,
account-name persistence, realm/options/addon dialogs, name/randomization controls and screen transitions.

Resolve current winning root/locale entries when extracting the interface; older RaceGuide snapshots
are references. `tools/login_screen_pack.py` and `tools/login_ui/` describe later Midnight/Sirus scene
work that must be included in the current extraction audit. Optional unrelated integrations such as
Freeborn need guarded UI bindings, so installing the complete interface does not require those systems.
Generate visible race/class/gender entries from the selected contract while retaining the Esteria layout.

Merge supported foreign Glue replacements or report an unsupported conflict. Full-file replacement is
safe only on declared baselines with backups. A minimal/stock alternative can be considered later;
it does not replace the required complete Esteria interface in the initial module scope.

#### Operator-configurable login and character-select logos

Ship the current Esteria artwork as the default and allow operators to replace the login and
character-select Esteria logos independently, or provide one image for both. Expose separate build/
installer settings for logo input, rendered width/height, anchor/offset and aspect-ratio handling.
These settings belong to the generated client branding profile; a server `.conf` entry alone cannot
change a pre-login texture on remote clients.

Convert supplied images into a validated 3.3.5a-compatible BLP or supported TGA with transparency,
and package them under module-owned names such as `Interface/Glues/EsteriaRaces/Branding/LoginLogo`
and `CharacterSelectLogo`. Generate the corresponding Lua/XML bindings through one branding layer.
Preserve existing fade/transition behavior and UI anchors; do not require operators to edit Lua/XML
or binary archives manually. Missing/invalid replacement input must fail staging with a useful error,
and the default profile must remain reproducible.

Historical login code binds `Config.LOGO_TEXTURE`; select XML binds `CharacterSelectLogo`. Both can
reference the common `Glues-WoW-WotLKLogo` asset, which other dialogs also use. Identify the current
effective bindings and separate these two brand slots rather than replacing that shared texture
globally. Alliance/Horde/Freeborn badges, race portraits and credits/dialog logos retain their own
ownership unless explicitly configured. Record logo inputs/output hashes and layout in the release
manifest, deliver them in both effective root/locale paths where needed, and support later rebranding
as a UI-only update with rollback that preserves character state and selected races.

Loose addon inspection found DragonUI, EsteriaChat, PlayerBots/SquadControl, ConsolePort and others.
Their presence is recorded in the inventory, not proof that race creation needs them. DragonUI's current
character portrait code uses `SetPortraitTexture` and its paperdoll backgrounds use UnitRace/file-string
paths; provide a selectable adapter/assets for this presentation. Offer a small standalone race display
addon where custom in-game portraits/names require hooks, rather than making the whole UI mandatory.

The existing export support script does not copy all loose addons, and its asset packer excludes loose
addon traversal. Implement separate TOC/dependency-aware addon packaging. Include matching addon code,
textures/fonts and dependencies for selected features; keep user settings and unrelated addons intact.
Normal addons cannot replace Glue loading, native race capacity or packet/appearance hooks.

Eluna/AIO is mounted from `mod-worgoblin-high-elf/lua_scripts` in the current environment. Audit the
actual race-facing handlers and payloads. Port required behavior into C++ where practical, or declare
an explicit optional Eluna/AIO adapter; do not make an unrelated progression UI an implicit prerequisite.

Keep Freeborn third-team logic, first/last names, cosmetic-wing trailers,
classless systems, stock HD replacements and stock Ascension customization as named optional features
or separate module integrations. Race essentials must work without them. Expanded character capacity
and the full Esteria Glue UI are included module features, not optional external dependencies.
Custom starting zones under `Harvested/Custom_Starting_Zones_Isolated_2026-10-04` can become optional
race content packs with map/area/SQL/map-vmap-mmap dependencies; current donor starts remain the default.
Mounts/forms/totems belong only when used by that race's functioning abilities/start policy.

### 4.8 More than ten characters: server, executable and roster UI

Install Esteria's expanded character capacity alongside every selected race set. The first release
targets **100 ordinary characters per account and 100 per realm**, with operator-configurable limits
within the validated release contract. Account-wide and per-realm limits are distinct; both must be
configured because increasing only the account-wide total can leave a ten-character realm bottleneck.

The current implementation is described in [100-character support](../../../docs/100-character-support.md).
`src/server/game/World/WorldConfig.cpp` and the distributed worldserver config default to:

```ini
CharactersPerAccount = 100
CharactersPerRealm = 100
```

Current realm validation accepts 1–100 and account validation requires account capacity >= realm
capacity. The installer must handle a stock target's lower validation ceilings/defaults through the
minimal core adapter, then set both effective server values. The generated selection/release profile
records both limits and the client roster capacity. Per-account totals across multiple realms must
respect the shared auth accounting policy; never describe the per-realm cap as the account-wide cap.
`HeroicCharactersPerRealm` remains a separate Death Knight limit unless explicitly changed.

Audit creation checks in CharacterHandler and the related restore, transfer, player-dump and optional
playerbot hiring paths. All applicable paths must enforce configured limits consistently. The existing
100-character contract fits the `uint8` SMSG_CHAR_ENUM count and unsigned tinyint auth
`realmcharacters.numchars`; it needs no character-count schema widening. Raising capacity beyond the
validated 100 target is a separate protocol/storage/UI audit, not an implied feature of this module.

Install the matching guarded client modification, not just worldserver configuration or a scrollbar.
Historical build-12340 evidence identifies the enum comparison at file offset `0x6404C`, whose limit
byte at `0x6404F` changed from `0x0A` (10) to `0x64` (100). Current capacity-extension source checks
that limit at VA `0x00464C4F` and preserves it. These addresses are evidence for the verified images,
not universal offsets. Add an explicit character-limit step to each supported executable patch profile,
validate complete instruction fingerprints and input/output hashes, and compose it with foundation,
appearance and archive-capacity changes. Refuse an unknown executable before modifying it.

The transplanted ECS/CharacterSelect UI must enumerate and reach the entire expanded roster through
scrolling/virtualization, keep create controls accessible below ten and below the configured limit,
and disable creation appropriately at the server limit. Preserve actual character indexes across scroll,
search/reorder and service actions, including entries above index ten. Its visible row count is not the
character capacity. Bound persistence shards/notes/order for the full target roster and preserve the
HXE1/HXE2 appearance trailers and optional cosmetic integrations at that size.

Install/release receipts must record server account/realm limits, executable patch state, roster UI
version and old values for rollback. A capacity reduction must not delete characters or silently make
existing excess characters unreachable; retain access while restricting new creation, or block an
incompatible downgrade until an explicit migration is prepared. Full server/client/Glue rollback needs
the same existing-character preflight as race removal.

## 5. New repository architecture

The following is a proposed structure, not a module created by this documentation task:

```text
mod-esteria-races/
  README.md, LICENSE, THIRD_PARTY.md
  CMakeLists.txt / include.sh / module loader (matching pinned AC conventions)
  conf/mod_esteria_races.conf.dist
  src/                      # policy, scripts, startup and diagnostics
  data/
    registry/               # reconciled identities, allocations, schemas
    sql/                    # module-owned shared schema/version migrations only
    races/<species>/        # manifests, DBC deltas, SQL recipes, stable codecs
    features/               # required Glue/branding/roster; optional zones/names/cosmetics
  integration/
    acore/<revision>/       # small checked core patch, compatibility metadata
    playerbots/             # optional revision-specific adapter
    eluna/                  # optional adapter, if required
  client/
    native/                 # appearance and capacity/select source
    profiles/12340/         # accepted executable hashes/site guards/patch graph
    glue/                   # complete Esteria login/select/create/customize and merge adapters
    branding/               # default logos, image conversion and operator branding profiles
    addons/                 # standalone race display and optional UI adapters
  tools/
    inspect, resolve, generate, stage, install, verify, update, rollback
  tests/                    # meaningful generator/core/native/protocol checks
  docs/                     # compatibility, development, migration and acceptance
```

Distribute large converted game assets as versioned race packs with immutable manifests and hashes,
outside normal Git history, plus a shared pack for the complete Glue/interface/runtime dependencies.
These payloads are mandatory release components, automatically installed for the resolved selection.
The code repo owns recipes, schemas, runtime sources and references to pack versions; the published
release supplies their actual bytes, including a complete offline bundle. Record source provenance/
licensing per component before deciding which inputs can be
redistributed; supplied binaries do not imply available source or blanket redistribution permission.

Use the official module skeleton/conventions for the pinned target. A server module normally requires
reconfiguration/recompilation after installation, as described in
[AzerothCore's module installation guide](https://www.azerothcore.org/wiki/installing-a-module).
This draft does not authorize or run those builds.

### Core boundary

| Keep in module/tooling | Keep in minimal core adapter until upstream hooks cover it |
| --- | --- |
| Race manifests, enabled identity set and feature policy | Race storage/index capacity and safe mask call sites |
| Race racial scripts and applicable Player/Unit hooks | ObjectMgr race/start/stat initialization extension points |
| Race startup/DBC generation and owned SQL | Create/enum packet parsing and extension transport |
| Appearance descriptors/validators through adapter API | Character DB prepared statements and save/load integration |
| Diagnostics and startup compatibility checks | Unit/Object update-field propagation and visibility |
| Optional bot/Eluna adapters | Needed DBC after-load/continuation APIs or stock-store integration |
| Branding/Glue/roster generation and capacity settings | Character-limit validation and related core paths |

Do not ship the broad `server-since-core-import.patch` as the race adapter. It includes unrelated
Eluna/playerbot/Freeborn/classless and server work. Reconstruct a minimal race-only delta against a
pinned upstream revision, then document adapters for additional revisions. A generic runtime policy
API should replace compiled per-race switches over time. A first version may generate compiled tables,
but must generate both sides from one allocation lock and document when selection changes require rebuild.

## 6. Race manifests and selectable installation

Use one schema with stable species keys and separate faction identity records. Each manifest declares:

- Identity: preferred IDs, file strings, visible/localized names, faction, start profile and paired identity.
- Dependencies: asset pack hashes, runtime capabilities, optional features and required shared assets.
- Art: model/display graph, authored genders, scale/bounds, equipment prefixes/coverage and animations.
- Appearance: stable source choice IDs, versioned codec, counts/defaults/requirements, excluded scopes.
- Server policy: enabled classes, gender validation, languages, stat/totem donors, startup/racial data.
- UI: creator ordinal mapping, portrait/background/lore/racial keys, locale support and adapters.
- Data ownership: DBC/SQL row keys/ranges, reference rewrites, migrations and conflict predicates.
- Acceptance: source acquired, converted, staged, installed, runtime checked, live accepted, with receipts.

Support `all`, named species, faction identities and saved presets. One species can select either or both
factions. Dependency resolution adds required shared capabilities/assets without enabling the donor as
a playable race. For example, Skyborne's High Elf eligibility donor may require donor metadata, not a
visible High Elf creator button. The resolved plan must list this distinction clearly.

Selection should be a single lockfile used to generate server policy, SQL, full DBCs, creator metadata,
native catalogs and runtime configuration. A server `.conf` switch alone cannot remove client rows or
implement a smaller package. Runtime configuration may narrow the release's permitted creation set;
enabling content absent from the release must fail with a diagnostic.

The same lockfile also records the complete Esteria Glue version, login/select branding profile and
account/realm/client character capacities. Race selection does not exclude these shared features.
Rebranding and roster policy changes produce matched outputs without regenerating unrelated race art.

### Allocation strategies

1. **Esteria migration mode:** preserve current numeric identities and frozen codecs; refuse conflicts.
2. **New-target mode:** prefer stable IDs, inspect collisions, then allocate free IDs and remap the entire
   graph from one lockfile. Generate native/server mappings so hard-coded race switches cannot drift.

Never renumber existing target characters as an automatic conflict fix. Foreign ownership of a race,
display, spell, sound, portrait or table key requires a merge policy or a different free allocation.
Legacy 32-bit donor masks do not give every installed race an independent bit; narrow actual identities
for custom admission/disable policy. Stock/public NPC DisplayRace values must remain distinct from
playable RaceIDs.

For shared resources, maintain ownership/reference counts. Removing one Ogre faction must not remove
models required by the other. Rebuild merged shared catalogs from installed owners plus the selection;
do not truncate another module's profiles. Generate canonical output ordering for reproducibility.

## 7. Portable installer design

Illustrative commands below define the intended interface; **they do not exist yet**:

```text
racepack inspect --server <path> --client <path>
racepack plan --preset all --profile stock-12340-enUS
racepack plan --races highmountain,earthen:alliance,gnoll
racepack plan --preset all --login-logo <image> --select-logo <image>
racepack plan --preset all --characters-per-account 100 --characters-per-realm 100
racepack stage --selection selection.lock.json --output <staging-path>
racepack install-server --stage <path> --target <path>
racepack install-client --bundle <path> --client <path>
racepack verify --receipt <path>
racepack disable-creation --race gnoll
racepack rollback --receipt <path>
```

### Installation lifecycle

1. **Inspect:** AC revision/fork/module ABI, DB schemas/updater receipts, executable architecture/hash/
   imports, WXL loader/extensions, locale, active archive order/loose overrides, effective DBCs, mount
   targets, foreign IDs and existing custom characters. Separate client/server inspection if remote.
2. **Resolve:** select identities/features, validate source availability, freeze allocation/codec/runtime
   versions and list foreign conflicts. Produce a reviewable plan containing all destination paths.
3. **Stage:** prepare minimal core patch, generated module configuration, scoped SQL, server DBCs,
   matched native runtime, complete selected asset closure, full Esteria Glue, converted configurable
   logos, expanded roster support, merged client DBCs and addon outputs.
   No live path writes during generation. Existing packers are recipes, not generic installation APIs.
4. **Verify stage:** data ownership/references, codecs, hashes, archive entries and supported image guards.
   Require a complete asset ledger and zero unresolved reachable dependencies on a clean baseline.
   Core/native builds and applicable tests happen in release CI or explicitly authorized development.
5. **Backup:** executable/import chain, replaced files/archives, DBC destinations, affected DB rows/schema
   and old selection. Store backups outside mountable Data. Check space for staging and rollback.
6. **Apply:** require closed client/archive editors and planned server maintenance. Install module/core
   integration, perform required server compilation, apply only selected owned migrations, deploy DBCs
   to actual mounts and install the matched client bundle. Use temporary files and verified replacement.
7. **Verify installed:** read effective entries through the real resolver, hashes, runtime load status,
   DB migration state and server readiness. Require fresh client start and named live acceptance.
8. **Receipt:** retain old/new hashes, selected races/features, allocation/codec versions, core/client
   profile, changed rows, updater state, log paths, acceptance gaps and rollback locations.

Always include the branding and account/realm/roster contracts in inspection, staging and receipts.
Client UI/executable capacity must support the configured realm cap; detect existing accounts above
requested lower limits before applying a downgrade. Operator-supplied artwork must be bundled in the
player release, rather than leaving local image paths in generated Glue files.

Filesystem and MySQL cannot form one ordinary ACID transaction. Use a durable operation journal with
idempotent phases and compensating restoration. MySQL schema DDL can commit implicitly; back it up
and define explicit downgrade behavior instead of promising transactional ALTER TABLE rollback.
On partial failure, resume or roll back from the journal; do not leave a silently mismatched release.

### Executable patch profiles

Each supported profile must define base hash/build/architecture, input→output hashes per step, exact
site guards, dependencies/order, exports, character-limit changes, incompatible features and rollback.
The current native patch
expects the old foundation hash; feeding a later archive-repaired or already-patched image to it is
not valid. A patch graph must compose foundation, appearance and archive repairs from verified bases.

Ship transformations applied to the user's supported executable, with matched runtime releases.
Keep a known customized-baseline profile for migration while developing a clean-stock profile.
Already matching outputs should be recognized idempotently. Unknown images stop before writes and
produce diagnostics. Do not ship an old `Wow.exe` during a catalog-only update.

### Database and DBC installation

Use operator-supplied connection/database names; remove hard-coded `ac-database`, credentials, Docker
container names, workstation drives and existing character GUIDs from generic tools. Support direct
SQL and a separate container adapter. Never recreate a populated world/characters database.

Separate fresh install, Esteria import and upgrade recipes. The module updater may discover SQL at
startup, so do not put every optional race's unconditional seed data into one automatically scanned
directory. Apply versioned shared schema normally and generated selected data through an owned,
receipt-backed installation step. Do not infer that a pending updater receipt is unapplied.

Preserve target class/racial/spell modifications by ownership and explicit conflict handling. The broad
export of 84,497 shared `playercreateinfo_spell_custom` rows is evidence, not a seed file to overwrite
another server's progression. Derive selected-race requirements instead of importing the whole dump.
Only extend `extraAppearance` schema when the resolved release needs it; do not import a captured
`CREATE TABLE characters` schema into an existing characters DB.

Respect repository SQL policy while developing: new SQL only in approved pending directories here.
Future standalone module-owned SQL layout follows the module's pinned AC conventions.

### MPQs, locales, addons and delivery

Separate per-race asset packs from one generated shared DBC/UI overlay. A bare `Races.MPQ` filename
is not automatically discovered by stock WoW. The installer chooses supported mounted names or merges
into reviewed winning archives, then proves effective precedence, including locale copies. Include
the complete Esteria Glue/interface assets and configured login/select logos in that effective graph. Do not
assume alphabetic “last patch” works on every loader. Check archive-count constraints separately.

Install required loose runtime/catalog files outside MPQs; addons go under Interface/AddOns with
preserved settings and checked TOC dependencies. Never pack binary catalogs as if the native helper
will automatically load them from an archive. Never copy WTF/account data or caches as installation inputs.

Server installation produces a redistributable client bundle and manifest. A player installer applies
that exact release locally. The existing launcher/CDN manifest work can be an optional delivery adapter;
the race module must also offer an offline ZIP/installer path without requiring Esteria's launcher or
services. Source acquisition/conversion tools are developer dependencies; normal users receive tested
converted packs and native binaries rather than needing Blender/CASC/Visual Studio.

## 8. Migration work plan and concrete deliverables

| Phase | Work | Completion criterion |
| --- | --- | --- |
| 0: Freeze evidence | Audit source/runtime/MPQ/DB/mounts/characters | Matched baseline, receipts and gaps |
| 1: Reconcile identities | Resolve conflicts/omissions/gender drift | One unambiguous ownership ledger |
| 2: Extract assets | Split closures; refresh newer work | Selected assets resolve on clean baselines |
| 3: Server module | Extract scripts/data/codecs and core adapter | Minimal AC creates selected races |
| 4: Client runtime | Vendor sources; develop executable profiles | Reproducible guarded transformations |
| 5: Generators | Schema/locks, full Glue, logos, roster and race data | Deterministic matched outputs |
| 6: Installer | Inspect/stage/back up/install/update/rollback | Fresh/upgrade/failure recovery verified |
| 7: Releases | CI, compatibility and live validation | Promoted races meet acceptance |
| 8: Esteria migration | Replace race dependencies incrementally | Existing characters/appearances preserved |

Start with representative pilot packs: High Elf for a legacy donor graph, Gnoll for native five-byte
creature appearance, Earthen for six-byte transport, Haranir for uint64 and Kobold for faction-local
shared-body choices. Add the other families after the complete generator/installer contract works.
All races remain in scope; pilots establish the architecture rather than defining a reduced final product.
Asset extraction includes all portrait/Glue/scene/addon/runtime dependencies and produces actual release
packs, a per-file ledger and the offline bundle. Complete closure on the clean baseline is a phase gate.
Each pilot includes the complete Esteria Glue package, independent logo replacement and the expanded
server/client character contract, so these shared features are validated before the full race release.

Use existing tools instead of rewriting proven converters/packers. Refactor common DBC/StormLib/
portrait/catalog/codec functionality into parameterized services. The inventory indexes all related
scripts, including `retroported_race_pack`, `expanded_appearance_pack`, individual race packers,
equipment/animation repairs and deploy tools. Existing deploy scripts often reject existing race
characters or rely on exact Esteria stages; preserve their evidence, replace their installation contract.

## 9. Validation and acceptance contract

No checks in this section were executed for the draft. They are required future implementation/release work.

| Layer | Required checks |
| --- | --- |
| Manifest/allocation | No collisions/duplicate owners/dangling references; complete gender/class policy |
| Selection | all/single/species/faction/subset; shared dependency reuse; disabled creation rejected by actual ID |
| DBC/assets | Valid layouts/strings, sorted CharSections, complete model/texture/animation/sound/visual graph |
| Asset completeness | Actual payloads, recursive/dynamic references, offline bundle and clean-baseline closure |
| Native runtime | Exact image guards, ID boundaries 63/64/127/128 and reject 129, missing/truncated/invalid catalogs |
| Appearance | Every changing option, dependency/randomizer rules, preview rollback, frozen codec round trips |
| Protocol/storage | HRC1/HXE1/HXE2 mixed/truncated cases, uint64 high bits, create/save/load/enum/nearby consistency |
| Server behavior | Languages after relog, racials, class starts, skills/actions/stats/totems/forms and faction rules |
| Glue/addons | Stock↔expanded resets, ordinal identity, locale precedence, portrait keys and foreign UI adapters |
| Character Select | Search/reorder real indexes, enter/delete correctness, mixed roster, repeated refresh/teardown |
| Branding | Independent login/select logos, alpha/aspect/anchors/fades, default fallback and rebranding rollback |
| Login/Glue | Current scenes, preview/Apply/Cancel, saved choices, dialogs and select/create/customize transitions |
| Character capacity | Create/select/login beyond ten; full 100 roster; realm/account limits and restore/transfer |
| Equipment | Bare/equipped body, helmets/hair hides, robes/boots/feet, shoulders/belts/cloaks and removal restoration |
| Installer | Fresh/upgrade/idempotent rerun, foreign file conflicts, low-space failure, interrupted journal recovery |
| Rollback | File/DB coherence, retained characters, codec compatibility, no restoration over later unrelated changes |
| Optional integration | Playerbots, Eluna/AIO, Freeborn, cosmetic wings and alternate loader/UI combinations |

Existing native harnesses include `TestNativeAppearance`, `TestHighmountainMaterials`,
`TestCustomizationChoices`, `TestRaceCapacity`, `TestArchiveCapacity` and `TestCosmeticWings`.
Existing Python race/packer tests and e2e protocol cases can be adapted, removing workstation/live-DB
assumptions. A passing harness cannot certify actual rendering or a complete clean installation.

Live acceptance for each promoted gender/faction covers create, customize, first login, languages,
movement/combat/cast/social animations, nearby-player appearance, equipment on/off, barber behavior,
logout/relog, roster selection and full client exit. Include ordinary-race regression and server rejection
of a manually submitted disabled identity. Tests above 63 must use real installed race packs, not just
a boundary harness. Recheck on the exact release binaries/assets rather than earlier screenshots.

For expanded capacity, exercise 10→11 and 99→100 creations, rejection at the configured limit,
selection/login/delete/service actions on entries above ten, and account totals across multiple realms.
Test full-roster scroll/search/reorder and persistence after restart. For the transplanted login UI,
verify current scenes and dialogs, preview/cancel/apply/restart, and independent replacement of both
logos at multiple resolutions with transparency, fades and layout preserved. Rebranding must leave
race data and character appearances unchanged; capacity rollback must preserve access to existing rosters.

Historical guide records confirm portions of Mag'har/Skyborne/Highmountain/Earthen/Haranir acceptance,
but leave final Mechagnome/Vulpera/equipment/exit scenarios pending. Haranir feet were explicitly deferred.
Current Vrykul/Naga/newer ports supersede older guide descriptions and need current receipts. Carry those
states forward honestly; do not label every family live accepted merely because it was extracted.

## 10. Disabling, removing, updating and rollback

Distinguish disabling creation, hiding a creator button, removing art and migrating a saved identity.
A hidden race can still be requested by packet; server enforcement is necessary. A disabled creation
policy can safely retain existing characters and their assets/codecs. Removing a race with saved
characters needs an explicit block or reviewed identity/appearance migration, not automatic deletion.

Upgrade by module release, core ABI, client runtime ABI, catalog version, data version and codec version.
Keep client/server compatibility tuples in receipts. A new selection may require generated header/native
changes and recompilation until those mappings become fully data driven. Deployment must not silently
enable missing content or send extended appearance to an unmatched client.

Before rollback, check that installed files/rows still match the receipt. If later foreign modifications
exist, stage a three-way restoration or stop with conflict details. Restoring an old schema/codec while
newer characters exist is not safe; retain compatible storage or migrate them explicitly. Restore matched
executable/DLL/catalog/DBC/UI/DB state, including character appearance remaps where required.

## 11. Release blockers and decisions

The following are concrete work items, not reasons to abandon the module:

1. A reproducible clean-client foundation or new stock-12340 backend; current guards target Esteria.
2. A minimal supported-upstream core adapter rather than the broad Esteria core snapshot.
3. Reconciled identities, including Furbolg ownership and registry omissions, preserving saved characters.
4. Refreshed export for current runtime, Kobold/Arakkoa/Drakonid and later repair state.
5. Reachability classification/fixes for known missing texture/model references.
6. Exact loader/vendor dependency and source/provenance audit, including proxy conflicts.
7. Portable selected-race generators replacing hard-coded paths, GUID migrations and Docker assumptions.
8. Named live acceptance for the actual standalone release and supported locales/platforms.
9. Complete current Glue extraction, independent logo configuration, and matched 100-character installation.
10. All required asset payloads bundled/installed, with zero unresolved reachable dependencies on a clean baseline.

Recommended first release defaults: stock faction teams, donor start zones, explicit per-race class policy,
preserved codecs, no classless/Freeborn/first-last-name requirement, complete current Esteria Glue UI,
replaceable login/select logos, and 100-character account/realm support with the matched executable and
roster UI changes. Provide all reconciled races and selectable subsets through the same manifest/installer
pipeline. Keep incomplete/experimental entries visibly marked until they satisfy their acceptance contract.

## 12. Reference module comparison and sources

The linked [Medviten module](https://github.com/Medviten/mod-worgoblin-high-elf) is useful precedent:
its documented installation combines a server module, core patch, optional bot patch, selectable DBC
preparation and a client archive/executable requirement. It is currently described as work in progress.
Adopt the idea of selectable content and merged DBC generation. Our release needs stronger ownership,
target inspection, appearance transport, executable profiles and recovery to carry Esteria's extra work.

The proposed core/module boundary is an inference from current source call sites, not a claim that
upstream already exposes every needed hook. Validate it against the chosen upstream revision while
implementing the adapter. Use the [official module skeleton](https://github.com/azerothcore/skeleton-module)
and [module installation documentation](https://www.azerothcore.org/wiki/installing-a-module) for that
revision's conventions. External sources were consulted October 14, 2026; local source hashes and
historical package receipts are preserved in the companion inventory.
