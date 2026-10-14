# mod-esteria-races implementation requirements

Status: normative target behavior. This document specifies future implementation; it claims no deployment.
Use [DESIGN](custom-race-module.DESIGN.md) for technical contracts and
[VALIDATION](custom-race-module.VALIDATION.md) for requirement evidence.

## Required product

| ID | Requirement |
| --- | --- |
| R01 | Install every reconciled custom race, or selected species/faction identities, from one distribution |
| R02 | Install on pinned supported AC revisions and clean/supported modified x86 build-12340 clients |
| R03 | Supply and automatically install every required non-stock asset and native runtime dependency |
| R04 | Transplant the complete current Esteria login/select/create/customize Glue UI and dependency graph |
| R05 | Provide independent replaceable login/select logos with generated asset and layout configuration |
| R06 | Install 100-character account and realm support, with matching executable and roster UI changes |
| R07 | Preserve actual identity independently of creator ordinal, donor masks, visual donors and faction |
| R08 | Preserve installed appearance codecs and supported authored choices across save/load and upgrades |
| R09 | Install functional starts, languages, racials, classes, stats, outfits, actions and required forms/totems |
| R10 | Generate full effective DBCs/catalogs/UI without overwriting foreign ownership or unrelated rows |
| R11 | Provide preflight, staging, backed-up install, update, resume, verification and coherent rollback |
| R12 | Preserve existing characters; distinguish creation disable from hidden UI and content removal |
| R13 | Include automatic pack retrieval plus complete offline selected/all release bundles |
| R14 | Produce deterministic matched outputs and versioned file/row/codec/runtime receipts |
| R15 | Keep unrelated Esteria systems optional; shared required UI/capacity/assets install for every subset |
| R16 | Establish clean-baseline and named live acceptance before promoting a race/profile to supported |

## Scope and baseline

The race ledger must cover the full inventory in [EXTRACTION](custom-race-module.EXTRACTION.md), not
only recent RetroPorter manifests. Preserve current stable identities on Esteria migration. On fresh
foreign targets, allocate collision-free IDs and regenerate every referencing layer from one lockfile.
Do not silently omit ambiguous legacy families from `all`; resolve them before the complete release.

Initial compatibility targets are one pinned upstream AC revision on Windows/Linux servers, one verified
stock-12340 enUS executable profile, and the verified Esteria migration profile. Additional forks,
locales/loaders/Wine are separately versioned support profiles. “Any server/client” is the portability
objective; an unknown executable or fork must produce a diagnostic before writes, not bypass guards.
The upstream SHA and clean-client hashes are I01/I08 outputs and must not be fabricated in these docs.

Normal stock client archives and ordinary AC base data are baseline inputs. Everything required by
installed functionality that is absent from those inputs must be bundled or generated from bundled
inputs. Donor patches, developer paths and caches cannot be installation prerequisites. Developer-only
conversion/acquisition tools may remain separate; operators receive converted asset packs and binaries.

## Mandatory shared features

Every race subset includes the complete current Esteria Glue package and expanded character capacity.
Preserve ECS real-index selection, filtering/reorder/notes, current login scenes/dialogs/transitions,
customization dropdown preview/cancel/commit, dependencies/randomization and stock-race resets.
Race selection changes metadata and available identities, not whether those shared features are installed.

Esteria logos are the defaults. Allow different image inputs for login and select, one input shared by
both, and explicit rendered dimensions/anchors/offsets preserving aspect/transparency. Generate supported
BLP/TGA and dedicated bindings; never globally replace a shared Wrath-logo texture used by other dialogs.
Rebranding is a UI-only update preserving race/appearance/DB state.

Default `CharactersPerAccount` and `CharactersPerRealm` are both 100. Account cap must be >= realm cap;
the client must support the configured realm roster. Test account accounting across multiple realms.
The initial supported portable contract caps both at 100; it may narrow settings but must not silently
reduce an existing host cap or make excess saved characters inaccessible. Lowering incompatible limits
requires a diagnosed migration/retention policy. Death Knight limits remain independently configured.

Freeborn, first/last names, classless progression, wing cosmetics, launcher/CDN, bot/Eluna integration,
stock HD replacements/customization and custom start zones are optional unless a selected feature
requires their declared dependency closure. Full Glue uses guarded bindings when an optional system
is absent. Only race-related behavior is extracted from larger modules.

## Required invariants

- Race IDs 1–128 are within the existing client capacity; 0 is none, 129 is rejected. Empty slots are not races.
- Stock RaceIDs and NPC DisplayRace values remain distinct; reserved NPC identities stay non-playable.
- Legacy masks stay bounded 32-bit donor aliases. Identity membership controls creation and custom admission.
- Player display IDs remain below 65536. A model row ID is a different allocation.
- Freeze stock-five, six-byte and five-plus-uint64 codec semantics; no silent choice reordering or data loss.
- Share allocation, stable choice IDs, codec descriptors and release digest across server/native/Glue generators.
- Preserve HRC1/HXE1/HXE2 boundaries and mixed rosters, padding ownership and native component lifetimes.
- Sort client CharSections into contiguous race/sex/section/variation/color groups.
- Require exact executable/site guards; keep accepted teardown and archive-capacity repairs.
- Generate mounted/effective tables from target data; preserve intentional client/server eligibility differences.
- Missing required assets, conflicting ownership or stale input hashes stop before target writes.
- Keep backups outside mountable Data; serialize MPQ writers and verify readback.
- No fresh-install GUID remaps, historical full-schema imports or unrestricted world DB resets on populated targets.
- Do not mutate existing bot rosters or unrelated server features as a race-install side effect.

## Definition of complete

All R01–R16 checks pass for the declared supported profiles. Every in-scope family has a reconciled identity,
complete closure, accurate capabilities and named live evidence on the actual release. Any deliberate
pre-existing feature limitations are recorded per race; they must not be hidden behind claims of Retail parity.
Required full Glue, replaceable branding, 100-character capacity and offline bundles pass independently
of whether a selected race uses extended appearance transport.

No complete release may depend on “copy these textures from the old client” or count unverified byte
extraction as gameplay acceptance. Documentation, code, runtime binaries, assets and generated data must
describe the same matched version. Release gates remain failed for missing mandatory profiles/assets/races.
