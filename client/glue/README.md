# Esteria Glue source

`client/glue/Interface/` is the module-owned source layout for the complete login/select/create/customize
interface. The checked `GlueXML.toc` is the exact winning Esteria TOC captured from
`Data/enUS/patch-enUS-Z.MPQ`.

The rest of the current Interface dependency closure is imported from the effective client stack by
`tools.racepack.import_esteria`. The importer follows TOC entries and Lua/XML file dependencies, resolves
static Interface/Sound/model/texture literals, records provider archives and hashes, and refuses to treat
the five currently unclassified MPQs as understood precedence.

Do not substitute `RaceGuide/sources/client-active` wholesale: several Lua files there differ from the
current effective client. Generated race metadata and independent login/select branding bindings will be
introduced here during I09 after identity reconciliation.
