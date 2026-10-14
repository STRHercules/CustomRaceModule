# mod-custom-races source installation

This is a development source module for ordinary AzerothCore WotLK. It has no CoA, Ascension,
playerbots, server-manager or repack dependency. The module uses standard AzerothCore script hooks
and config discovery. It is installed as `modules/mod-custom-races` and compiled with the host core.

**This package is the source foundation, not a playable custom-race release.** Its installed identity
set is currently empty. Enabling it cannot add races, patch the core/client, install DBCs or create SQL
rows. A matched core adapter, race data, assets and client runtime still need implementation and testing.
No configuration override bypasses those requirements.

## Install source

Use a separate AzerothCore checkout at commit `aa8a04c82ffc315277e93e937b4e6a0d7a6aba58`.
From the CustomRaceModule development repository, with Python 3.10 or newer:

```powershell
rtk proxy python -m tools.racepack inspect-core --core-root '<azerothcore-checkout>'
rtk proxy python -m tools.racepack install-module --core-root '<azerothcore-checkout>'
```

The installer checks the exact core revision and the pinned source text for the account/world hooks,
their creation call site, script dispatcher and module loader/config discovery. It creates a new module directory;
it refuses an existing module, either previous module name, modified contract files, or another core
revision. It writes no core source, databases, server binaries or client files and runs no build/services.
It copies and verifies source hashes before publishing the directory. Source installation is not a
durable deployment journal or the release installer specified by I12.

For an offline source directory, use `stage-module --output '<new-directory>'`. Its
`source-module.manifest.json` records each source file's size/hash and explicitly marks playable release
readiness false. Put that staged directory at `modules/mod-custom-races` on the pinned checkout;
manual placement does not perform the automatic core checks.

Configure and build AzerothCore using its normal instructions with `MODULES=static` or `dynamic`.
The host discovers `src/` and `conf/*.conf.dist`; no standalone module CMake project is required.
After the host install, copy `mod_custom_races.conf.dist` to `mod_custom_races.conf` in its modules
configuration directory. Keep `CustomRaces.Enable = 0` during development.

The pinned API and source layout were inspected. Full AzerothCore compilation and live acceptance
have not yet been performed for this module.

Source inspection and installation have been exercised on a separate sparse checkout at the pin;
the second installation was refused. The standalone C++ policy harness also compiled and passed on
MSVC 19.50.35730.0. These checks do not validate complete core/module linkage or playable races.

## Creation policy

`CustomRaces.CreationRaces` accepts `all`, `none`, or a comma-separated list of actual installed RaceIDs.
The generated installed set is immutable during config reload. Unknown, stock, duplicate and
out-of-range IDs are rejected, and invalid configuration disables owned custom creation. The master
switch affects only new creation of module-owned identities. Stock and foreign identities are passed
to the host's remaining checks. Login and existing character records are not changed by this hook.

Identity admission never uses a 32-bit race mask or wraps a RaceID above 32. Legacy donor masks remain
separate eligibility metadata. Gender/class validation, character service paths, persistence and extended
appearance need the core adapter; this account hook cannot replace them.

The old `mod-esteria-races` directory/config name is retired for new source installations. Do not install
both names. Raw Esteria snapshots and existing evidence locks retain their original names and hashes;
they are migration inputs rather than general host defaults. This source installer provides no upgrade
or removal of an existing deployment.

## Developer policy generation

Edit only reconciled definitions in `data/registry/server-policy.json`, then run:

```powershell
rtk proxy python -m tools.racepack generate-policy
rtk proxy python -m tools.racepack generate-policy --check
```

The strict loader rejects duplicate JSON keys, duplicate identities/IDs, unknown fields, unsupported
versions, stock ownership and invalid donors. Output is ordered deterministically and carries a
canonical policy digest. This admission schema is only the first part of I03; it does not define the
complete allocation, species, codec or release schemas. Adding an identity requires matched data/client
outputs and independent release evidence before readiness can be implemented.
