# Identity reconciliation

Status: I02 in progress. This file records decisions that are safe to make from the October 14, 2026
baseline without silently reinterpreting saved characters. The machine-readable companion is
`release/identity-reconciliation.json`.

## Evidence rule

Identity is not inferred from one registry. Reconciliation compares the effective client `ChrRaces.dbc`,
live mounted server `ChrRaces.dbc`, current Glue metadata, current C++ enum/registry/manifests, and aggregate
saved RaceID/appearance evidence. A saved RaceID is never reassigned merely because a stale manifest uses the
same number.

## Decisions already safe

Race 62 remains the active Alliance Sethrak. It has two saved characters and agrees across the current
client/server identity. Race 15 remains a legacy non-playable Sethrak identity rather than being exposed as a
second active race.

Race 29 is preserved as Alliance Kul Tiran. Races 30 and 31 are preserved as Horde and Alliance Illidari.
Those identities are missing from the older registry/core race block, but the effective client/Glue metadata
agrees and live saved characters exist on all three IDs. The module must add definitions for them rather than
drop them from the standalone release.

Race 61 remains Alliance Ogre. The current client, server, Glue and allocation data agree on that meaning.
The older Furbolg manifest still claims 61 and overlapping appearance/start allocations, so it is stale and
cannot take ownership back. Furbolg stays in scope but requires a distinct ID and new table allocations.

Race 71 is only a **candidate** for Furbolg, not an allocation yet. It is absent from the effective client
ChrRaces table, current race enum block, saved-character aggregates, registry/retroport manifests and targeted
race/native/Glue references checked so far. Full DBC/SQL/UI/native ownership checks and replacement table
ranges are still required before 71 can become stable.

Existing extended appearance data is a hard compatibility constraint. Race 48 has one saved extended value
(`43`). Race 51 has two saved extended values in the observed range `14347388583937` through
`111355737414930`. Their current codec definitions must be frozen and round-trip tested before generators are
allowed to emit replacement definitions.

## Blocking conflicts

IDs 24-27 are not constrained by saved characters, but the authored layers disagree sharply. The effective
client/server tables currently say 24 = Fel Orc, 25 = Broken, 26 = an empty placeholder, and contain no row 27.
The older registry/core sources instead call them Broken Alliance, Forsaken, Pandaren Horde, and Broken Horde.
The module will not pick one history silently. These four identities must be deliberately rebuilt together.

IDs 66 and 67 have a Drakkin/Kobold split. The current client and effective Glue call them Drakkin Alliance/
Horde, the retroport manifests are Drakkin, while the live server ChrRaces rows call them Kobold Alliance/Horde.
Race 66 has one saved character, so the numerical identity must be retained while the stable species naming,
asset ownership and pair policy are resolved. Race 67 currently has no saved character and is marked retired
in the older registry, but it cannot be finalized independently of 66.

## Release effect

I02 remains incomplete while any machine-readable `unresolved` entry exists. No `all` selection lock or
installer may consume a provisional candidate as if it were a stable identity. Raw Esteria files under
`vendor/esteria/` remain evidence; the final module-owned `data/registry/{species,identities,allocations}.json`
will be emitted only from the reconciled contract.
