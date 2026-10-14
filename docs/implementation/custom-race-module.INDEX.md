# mod-esteria-races implementation package

Status: implementation begun in CustomRaceModule; I01 baseline capture and I02 identity reconciliation are in progress.
Date: October 14, 2026. Working name: `mod-esteria-races`.

See [execution record](progress.md) and [initial targets](../compatibility/initial-targets.md) for actual
outputs, checks and unresolved gaps. This preserves the specification; no supported release exists yet.

Build a dedicated AzerothCore module distribution that installs all current custom races or a selected
subset, the complete current Esteria Glue interface, independent login/select branding, expanded account/
realm character capacity, and every required non-stock asset. Deliver a server module, a minimal checked
core adapter and a matched player-side client installer. The supported clean-client target is Windows
x86 WoW 3.3.5a build 12340; initial character capacity is 100 per account and 100 per realm.

## Read and execute in this order

1. [REQUIREMENTS](custom-race-module.REQUIREMENTS.md): binding scope, invariants and release criteria.
2. [DESIGN](custom-race-module.DESIGN.md): destination structure, interfaces, formats and install state machine.
3. [EXTRACTION](custom-race-module.EXTRACTION.md): existing sources, target ownership and unresolved identities.
4. [PLAN](custom-race-module.PLAN.md): ordered implementation tasks, dependencies, outputs and done criteria.
5. [VALIDATION](custom-race-module.VALIDATION.md): requirement traceability and evidence needed to release.

These five documents are the normative implementation instructions. The
[original analysis](../custom-race-module.ANALYSIS.md), [inventory](../custom-race-module.INVENTORY.md),
[machine inventory](../custom-race-module.INVENTORY.json) and [capture utility](../custom-race-module.capture.py)
remain supporting evidence. They do not override newer verified source or the requirements in this package.
The inventory captures a dated filesystem snapshot, not a certification of today's running server/client.

## First implementation action

Execute task I01 in PLAN: capture a fresh matched source/client/server baseline and pin the first upstream
AC revision and toolchains. Then I02 reconciles race identity before allocation or data generation.
Do not start by importing all historical SQL or copying the broad Esteria core diff into another server.
Do not describe unresolved clean-client compatibility as implemented.

Implementation should begin in a new isolated `mod-esteria-races` repository/workspace. Configure its path
explicitly; do not infer that this documentation request authorizes creating a GitHub repository, publishing,
deploying or changing the existing Esteria installation. A future request to implement can authorize the
local coding work. Builds, tests and deployment follow the instructions and authorization of that task.

## Document maintenance

Keep this package under `.agents/plans/custom-race-module/` while planning in Esteria. On module creation,
copy the normative documents to its `docs/implementation/` and update links to the preserved evidence bundle.
Do not replace the inventories with invented output paths or proposed schemas. Commit implementation docs
to the new module repository; these planning files are gitignored in the current repository.

Every task completion records destination files, input hashes/versions, checks actually executed and open
acceptance gaps. Task checkboxes remain unchecked until outputs exist and their done criteria are met.
The complete `all` release includes every reconciled in-scope family, including historical families such
as Furbolg. Pilot packs prove infrastructure; they do not satisfy the final all-races requirement.

## Known blockers with assigned work

| Blocker | Task |
| --- | --- |
| Clean-stock executable transformation/foundation source not established | I01, I08 |
| No pinned upstream minimal core adapter yet | I01, I06 |
| ID 61 Ogre/Furbolg conflict; 24–27 drift; omissions 29–31/67 | I02 |
| Historical export differs from later runtime/ports | I01, I04, I11 |
| Unresolved reachable asset references and vendor/runtime provenance | I04, I08, I11 |
| Final live acceptance of the standalone release | I13–I15 |

Resolve these through investigation and tested outputs. Do not weaken fingerprint guards, drop races,
discard authored choices or substitute development-client dependencies to make a task appear complete.
