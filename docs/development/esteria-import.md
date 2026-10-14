# Importing the Esteria implementation

`mod-esteria-races` must become self-contained without pretending the current Esteria checkout, development
client, or historical `Races/` export is a clean release artifact. `tools/racepack/import_esteria.py` is the
controlled bridge from those inputs into module-owned source/staging data.

## Inputs

Use explicit roots. The importer never infers Zach's workstation paths:

```powershell
rtk proxy python -m tools.racepack.import_esteria `
  --source-root 'R:\Users\Zach\Documents\GitHub\EsteriaWoW' `
  --client-root 'G:\3.3.5a - Dev' `
  --output-root '<empty-or-module-staging-root>'
```

Add `--include-runtime` only when intentionally staging loose DLL/catalog runtime candidates. Those files
are marked `redistribution_status=review_required` in the receipt. `--replace` is required to overwrite a
previously imported file whose bytes changed.

## Current import contract

`data/vendor/esteria-import.json` currently covers:

- 24 retroported-race allocation/manifests and the current race registry.
- Native appearance sources, material tables, tests/build recipes, and the character-select extension source.
- Five server appearance headers and the Broken/Worgen/Darkfallen racial source inputs.
- Thirteen race startup/schema reference exports that are small enough to preserve as extraction evidence.
- Ninety-three race, appearance, portrait, Glue, login, customization, repair, and conversion recipes.
- The recognized effective Glue/Interface dependency closure, extracted from the actual client archive stack.
- Optional loose client runtime candidates including Esteria catalogs, WarcraftXL, loader and required extension candidates.

A real-client staging run on October 14, 2026 copied 156 source/reference files, 74 Interface dependency files,
and 9 static Glue assets with zero unresolved static asset literals. Including runtime candidates added 42 files
and produced roughly 300 MB of staged content. These counts are discovery evidence, not a release guarantee.

## Raw evidence versus module-owned data

`vendor/esteria/` is raw input. Do not resolve conflicts by editing it. `vendor/esteria/source-lock.json` pins
files already copied directly into Git. The first checked inputs are the exact current allocation ledger and race
registry. `client/glue/Interface/GlueXML/GlueXML.toc` is the exact winning TOC from the current client.

I02 writes reconciled identities under `data/registry/`. Later generator stages consume those reconciled inputs,
not the raw registry directly. This is especially important for IDs 24-27, 61, 67, the old Sethrak identity,
and any saved-character codec ownership discovered during reconciliation.

## Glue source of truth

Do not bulk-copy `RaceGuide/sources/client-active/Interface/GlueXML`. Several Lua files in that folder differ
from the effective client even though the TOC and some XML files match. The importer reads the winning files
through `tools/racepack/wowio/`, follows Lua/XML dependencies into other Interface folders, extracts static
Interface/Sound/model/texture literals, and records the provider archive and SHA-256 for every staged file.

The current client still has five MPQs outside the recognized numeric/letter resolver contract:
`Data/common-3.MPQ`, `Data/enUS/backup-enUS.MPQ`, `Data/Patch-Dn.MPQ`, `Data/Patch-Dr.MPQ`, and
`Data/Patch-Zzz.mpq`. Their presence is emitted as a warning and remains an I01 precedence blocker.

## Large assets

The historical `Races/` tree is about 6.8 GB and the current loose runtime candidates include large generated
texture/catalog payloads. Do not commit those wholesale just to make the repository appear complete. I04 must
produce an asset ledger that identifies each required file as bundled, generated, or verified stock, with
provenance and ownership. Public/release payloads must not depend on the old `G:`, `R:`, `C:` or temporary
source paths embedded in historical manifests.
