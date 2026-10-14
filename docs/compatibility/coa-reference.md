# CoA reference and standalone module boundary

Inspected October 14, 2026. Reference repository:
`https://github.com/ilusixn/azerothcore-wotlk-coa`, branch `coa-custom-1.5-csm`,
commit **`760e404239693625eab940791b7036316adccf05`**. Branch names are mutable; these observations
refer to this commit. The reference was cloned separately; no live Esteria files were edited.

## Verified reference structure

| Component | Pinned reference path | Observed responsibility |
| --- | --- | --- |
| Module | `modules/mod-coa-custom-races/src/mod_coa_custom_races.cpp` | Config switch and account creation veto; also registers hide-armor scripts |
| Config | `modules/mod-coa-custom-races/conf/coa_custom_races.conf.dist` | `CoACustomRaces.Enable`, defaults enabled |
| Core race capacity | `src/server/game/Entities/Player/RaceMgr.{h,cpp}` | Playable DBC IDs, dynamic maximum, 32-bit faction/playable masks |
| Appearance IDs | `src/server/shared/SharedDefines.h` | Literal CoA RaceIDs 66/68/69 and Haranir 70/71 |
| Racials | `src/server/shared/CoaCustomRacials.h` | Generated 49-entry exact-ID racial spell table |
| Startup | `src/server/game/Globals/ObjectMgr.cpp` | Creation data capacity and exact-race racials |
| Protocol | `src/server/game/Handlers/CharacterHandler.cpp` | HXE1/HXE2 enum trailers and HRC1 creation appearance |
| Repack installer | `apps/coa-custom/install.py`, `README.md`, `manifest.json` | CoA server/client replacement, SQL, bots and repack settings |

The module README requires core patches, world SQL, server DBCs, client MPQs and native runtime DLLs.
Copying its module directory cannot implement custom races on stock AC. The repack README describes
120-character support; our existing distribution requirement remains 100.

`RaceMgr.cpp` computes `1u << ((raceId - 1) & 31)`. DBC eligibility also wraps, and other sites still use
direct shifts. A high actual RaceID must remain separate from its bounded eligibility donor. The
hardcoded appearance IDs also differ from the Esteria preservation ledger and cannot be copied onto
saved characters or a fresh allocation.

## Product direction

The public distribution is now **`mod-custom-races`**, configuration namespace **`CustomRaces`**.
Esteria supplies content and a migration profile; it is not the host server dependency. This direction
supersedes the historical working name in the implementation documents. Content scope, appearance
preservation, full adapted Glue, replaceable branding and 100-character requirements remain.
Generic default branding is still pending; the earlier Esteria-logo default is a source-profile setting.

| Part | General AzerothCore contract | Current state |
| --- | --- | --- |
| Server module | Standard loader/config, actual-ID ownership, creation narrowing, racial/startup scripts | Loader/config/admission foundation implemented; racial/startup extraction pending |
| Core adapter | Upstream pin, minimal missing capacity/protocol/storage hooks | Source API checked; adapter not implemented |
| Content packs | Species/faction policy, starts/racials, owned SQL/DBC deltas and assets | Source evidence exists; reconciliation and closure pending |
| Client | Guarded build-12340 runtime, generated choices/identities and adapted Glue | Importable inputs; matched runtime/installer pending |
| Installer | Target paths, selected/all stage, receipts and rollback | Source-only staging/installation implemented; release installer pending |
| Integrations | Optional CoA, playerbots, Eluna or progression adapters | No such dependencies in source module |

Use stock WotLK classes/progression as the general baseline; species/faction/class rules belong in
reconciled manifests. Special class systems and starts are optional adapters. Do not import CoA spell
numbers, racial balancing, Book of Ascension behavior, bot settings, Wardrobe systems, auction house
setup, whole world tables or its precompiled worldserver into the default product. Hide-armor is
optional cosmetic behavior and is not part of race admission.

The runtime installed set is generated policy. `CustomRaces.Enable = 0` vetoes owned custom creation
only; existing-character login is untouched. Foreign identities continue through the host/other modules.
`CustomRaces.CreationRaces` narrows installed content. Readiness is a compiled contract, not a config override.

## Remaining implementation order

1. Finish I02 reconciliation, preserving saved IDs/codecs; CoA would be a separate optional profile.
2. Complete I03 species/identity/codec/ownership schemas and shared matched definitions.
3. Extract race-only startup/racials and implement the I06 adapter against the upstream pin.
4. Build client/data packs with complete asset closure and required UI/capacity behavior.
5. Implement selected/all installation, rollback and isolated clean-server/client acceptance.

The admission policy is intentionally empty/unresolved. It does not drop any family from the eventual
`all` release or resolve open ID conflicts. Source staging is not release acceptance.
