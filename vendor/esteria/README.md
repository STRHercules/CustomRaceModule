# Esteria source snapshot

This directory contains raw, byte-preserved inputs imported from the EsteriaWoW implementation while
`mod-esteria-races` is being made standalone. Files here are evidence/source material, not the final
reconciled registry and not automatically installed as-is.

`source-lock.json` records the exact Esteria source revision and hashes for files already vendored. The
import contract at `data/vendor/esteria-import.json` describes the larger source/tool/runtime closure.
Run `python -m tools.racepack.import_esteria` with explicit source, client, and output roots to stage a
fresh copy and produce `release/esteria-import.lock.json`.

The importer currently covers the race manifests/registry, native appearance/select sources, appearance
headers, racial sources, startup database reference data, 93 legacy race/conversion recipes, the current
recognized effective Glue dependency closure, and optional loose native runtime candidates. Runtime DLLs
and large generated catalog/model/texture payloads remain redistribution-review inputs until provenance is
settled; they are not silently committed just because they exist in the development client.

Do not edit raw vendored files to resolve race conflicts. I02 writes reconciled module-owned data under
`data/registry/` and per-race module manifests while retaining these bytes as historical evidence.
