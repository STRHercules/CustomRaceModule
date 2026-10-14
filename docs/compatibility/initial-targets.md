# Initial compatibility targets

Recorded October 14, 2026. These are development targets, not supported release profiles.

| Input | Pin / observation | Acceptance |
| --- | --- | --- |
| Upstream AzerothCore | `aa8a04c82ffc315277e93e937b4e6a0d7a6aba58` | Adapter and builds not implemented |
| Esteria source HEAD | `a6f7e6d0a36b8f5bb6900a6cd79850ccb2c45bdb` plus frozen dirty inputs | Not equated to running server |
| Python tooling | Python 3.14.4, standard library | Unit tests executed |
| Git | 2.54.0.windows.1 | Read-only probes executed |
| CMake | 4.2.3-msvc3 | Version probed; configure not run |
| Windows compiler target | Installed MSVC toolset 14.51.36223, C++20 | Compiler/build not run |
| Linux compiler target | Not selected | Open I01 task |
| Client target | Windows x86 WoW 3.3.5a build 12340, enUS | Clean image/build/locale not certified |
| Character limits | Account 100 / realm 100 | Implementation and live acceptance pending |

The upstream pin was obtained directly with `rtk git ls-remote` against
`https://github.com/azerothcore/azerothcore-wotlk.git`, `refs/heads/master`. Its root CMake file, module
CMake file, module documentation and license were downloaded at that exact SHA and frozen with hashes.
This selects a concrete adapter target; it does not imply current Esteria modifications apply to it.

The pinned `modules/CMakeLists.txt` collects module sources and generates an
`Add<directory-name-with-hyphens-replaced-by-underscores>Scripts()` loader. It auto-discovers
`conf/*.conf.dist` and optionally includes `<module-directory>.cmake`. Use that revision's conventions
in I03 rather than assuming the older `AC_ADD_SCRIPT` API. Install-directory naming must match the loader.

Two explicitly supplied backup executables are identical, SHA-256
`a6bf4bfed8febdf0d50c345d1851869f91da1d709fe2572b71afa297be881ca7`, with PE machine `0x014c` (x86).
Their backup names do not establish a clean stock executable. Active `Wow.exe` has SHA-256
`b8d5b92d80ecf7044c07768d2df1171c345a34006c33afca7749247d63957e85` and matches the historical export.
I08 must establish build/locale, accepted image provenance, patch-site guards and foundation derivation.

The baseline freezes 287 source/runtime/reference files with readback verification. Three active shared
appearance artifacts differ from the historical export, and the Drakonid catalogs are absent from it.
All discovered extension DLL/JSON files are inspection candidates; presence does not imply dependency
or permission to distribute. The archive list has 59 entries, sizes only; it is not effective mount order
and has no archive-content hashes or extracted current Glue/DBC certification.

Remaining I01 work: effective client/server data, current server image/revision, read-only database
schema and aggregate saved identity/codec state, vendor provenance and concrete Linux toolchain pin.
Race-ID reconciliation follows these inputs in I02; do not allocate a new Furbolg ID or reinterpret
race 61 before saved-state evidence is available.
