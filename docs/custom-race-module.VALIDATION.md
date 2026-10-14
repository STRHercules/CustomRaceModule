# mod-esteria-races validation and release gates

This specifies future checks. No builds/test suites/deployments or live scenarios were executed while
preparing this implementation package. Read applicable build guidance and obtain the task's build
authorization before running them. Record exact artifact hashes and actual results, never inferred passes.

## Requirement traceability

| Requirement | Implementation tasks | Required evidence |
| --- | --- | --- |
| R01: all/selectable races | I02, I03, I11, I14 | Full ledger; all/single/species/faction output comparison |
| R02: portability | I01, I06, I08, I13, I14 | Pinned core and stock/Esteria profile patch/build/install evidence |
| R03: complete assets | I04, I08, I11, I14 | Per-file closure ledger; actual payload bytes; clean-baseline readbacks |
| R04: full Glue | I04, I09, I13 | Current UI extraction, TOC/wrapper contract and scene/control live cases |
| R05: branding | I09, I12, I13 | Independent logo conversion/layout/install/rebrand/rollback cases |
| R06: character capacity | I08, I10, I13 | Server/client boundaries, full roster, account and realm accounting |
| R07: identity | I02, I03, I05, I06 | Actual-ID admission, donor/ordinal distinction, collision rejection |
| R08: appearance | I03, I07, I08, I13–I15 | Frozen codec fixtures, mixed protocol, persistence and migration checks |
| R09: gameplay | I05, I07, I13, I14 | Languages/racials/starts/actions/skills/stats/totems/forms live evidence |
| R10: owned merges | I03, I07, I11 | Unrelated row preservation, ownership/reference and precedence reports |
| R11: safe install/recover | I12, I13, I15 | Interrupted phase recovery, before/after receipts and rollback results |
| R12: retained characters | I02, I05, I10, I12, I15 | Creation-disable/login, removal/downgrade preservation |
| R13: complete delivery | I04, I11, I12, I14 | Offline install without donor/developer inputs; online hash resolution |
| R14: reproducible versions | I01, I03, I07, I08, I11, I12 | Digests, input freshness and matched ABI receipts |
| R15: optional unrelated systems | I05, I06, I09, I13 | Minimal server/full Glue works without optional systems |
| R16: actual acceptance | I13–I15 | Exact-release static/runtime/live acceptance matrix and named gaps |

## Meaningful automated cases

**Schema/resolver:** duplicate identity/owner, foreign key collision, unsafe path, unsupported version,
overflow and unavailable required pack must fail before writes. Exercise shared owner removal and
species/faction/all selection. Donor metadata must not enable a donor playable button. Re-run with
identical semantic inputs and confirm digests/outputs; exclude volatile reporting fields.

**DBC/asset:** validate WDBC layout/string offsets, referential integrity, CharSections sorted groups,
preserved foreign records and semantic eligibility differences. Traverse embedded and generated paths,
SKIN/ANIM variants, native banks, Lua dynamic scene/portrait/equipment lookups and addon TOCs. Assert
zero unresolved reachable dependencies on clean stock archives. Reopen staged/installed archives and
verify ledger hashes through actual locale/loose precedence. Corrupt/remove one required pack and assert
staging aborts; an unused unreachable historical variant gets an explicit classification, not a fake file.

**Core/module:** verify pinned patch application/rejection and early initialization/linkage. Exercise
actual-ID disabled/gender/class creation with donor masks shared by enabled races. Stock identity
behavior must remain unchanged; selected starts/languages/racials use owned data and correct masks.
Check realm/account validation and all affected creation/restore/transfer/dump paths.

**Native/profile:** reuse/adapt TestNativeAppearance, TestCustomizationChoices, TestHighmountainMaterials,
TestRaceCapacity, TestArchiveCapacity and optional TestCosmeticWings. Validate 63/64/127/128 and reject 129,
unknown executable hash/site bytes, mismatched exports/catalog versions and already-patched images.
Preserve AL bool returns, stdcall allocator/lifetimes and component-free cache clearing. Tests must use
the actual DLLs/catalogs generated for the release, not a separately simplified implementation.

**Protocol/persistence:** encode/decode fixtures from frozen codecs, class/gender/prerequisite bounds,
uint64 high bits and valid defaults. Cover HRC1 length/magic/range rejection, mixed HXE1/HXE2 optional
CWG1 peeling, duplicate/missing GUID and malformed/truncated trailers. Save/load/enum/nearby updates
must preserve stable choices. Exercise existing choice-order upgrades and before-image rollback on
isolated data. Do not touch the production DB as a test fixture.

**Glue/branding:** validate TOC ordering, complete required files, generated-ID mappings, stock↔expanded
resets, hover/cancel/commit/randomization, dropdown wheel behavior and full roster index binding.
Convert transparent/non-square default/custom images; independent logo paths must not rewrite shared
dialog/faction artwork. Rebrand changes only owned UI payload/receipt fields, preserving native/server/DB
hashes. Current scenes must retain preview/apply/cancel/delayed-load/persistence behavior.

**Installer:** inject failures before/after every durable phase, including schema DDL, selected rows,
archive replacement and installed verification. Verify idempotent resume or coherent compensation.
Test low-space checks, changed baseline, open-client preflight, proxy collision, missing target mount,
foreign edits after install and offline pack availability. Record before-images and reject rollback
over later unrelated modifications. Verify remote server/client adapters do not assume one filesystem.

## Named live acceptance cases

Create an isolated supported stock client plus minimal pinned AC server using only released payloads.
Disable/move development patches, loose custom files and appearance caches out of resolution. Also run
the migration profile on a cloned Esteria baseline. Do not claim live acceptance from static extraction.

For every supported gender/faction/race, record release/profile/codec hashes and these cases:

1. Create with defaults and representative boundary choices; verify race/class/gender eligibility.
2. Cycle every changing control; exercise dependent options, randomizer and hover cancel/commit.
3. Switch expanded→stock→expanded; verify labels/materials/controls and no lost saved state.
4. Select/login/relog and nearby-client view; verify five/six/uint64 appearance persistence and high bits.
5. Chat in declared languages; exercise implemented racials and movement/combat/cast/social animations.
6. Equip/remove supported helmet/shoulder/robe/boot/cloak combinations; inspect bare/equipped body and feet.
7. Use existing legacy barber behavior and record its declared limitations accurately.
8. Repeatedly change roster selection, logout/relog and fully exit; include ordinary-race regression.

Shared features require these additional cases on a sparse selected race set and the all-races release:

- Current login scenes: initial display, delayed loading, preview/Cancel/Apply, restart persistence/dialogs.
- Independent login/select logo replacement, default branding, alpha/aspect/anchors/fades at multiple resolutions.
- Complete login→select→create→customize→select transitions with supported optional integrations absent.
- Create character 11 and 100; reject at configured realm cap; verify account-wide cap across realms.
- Reach roster entry 100 via scroll/search/reorder and perform selection/login/rename/service/delete on actual indexes.
- Persist full roster ordering/notes through restart; preserve mixed appearance trailers and correct preview models.
- Disable creation for one race, reject manual packet creation, retain login/rendering of existing characters.
- Rebrand, update subset/shared assets, remove one shared owner and roll back without altering other owners/state.

Observe destructive service/delete cases only on disposable fixture characters. A capacity reduction
must preserve existing-character access or be blocked, not truncate the roster. No invented model or
unimplemented racial claim can substitute for declared authored scope.

## Evidence format and release gate

Each `acceptance.json` case records case ID, R IDs, race/gender/faction, target core/client profile,
release/lock/DLL/asset/codec hashes, input setup, actual steps, expected/observed outcome, logs/screenshots
where appropriate, result (`pass`, `fail`, `not_run`, `not_applicable`) and limitation rationale.
Historical confirmations may inform test selection; they are not passes for a new release hash.

Gate G1: I01–I03 baseline/identity/schema complete, with no ambiguous selected identity.
Gate G2: required assets captured/generated/verified stock; reachable unresolved count is zero.
Gate G3: pinned core/native/DBC/Glue/capacity contracts verified on exact matched artifacts.
Gate G4: failure recovery/update/rollback and offline installation verified in isolated targets.
Gate G5: named live cases pass for all promoted races and mandatory shared features/profiles.
Gate G6: complete all-races/offline bundles, compatibility docs, provenance and checksums are reviewable.

The complete release requires all gates. Blocked mandatory races/clean-stock profiles cannot be marked
not applicable to obtain an all-races pass. Publish experimental artifacts under separate status if
authorized; do not label them the finished module. Repeat checks when the affected code/assets/contracts
change; avoid broad repeated testing after unchanged checks already pass.
