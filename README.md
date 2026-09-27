# Snap64 Recomp mod template

A working example of a mod for [Snap64 Recomp](https://github.com/JackandBeans/Snap64Recomp),
and the files to start one of your own. A mod is code that runs inside the
recompiled game: it can hook a game function, run after one, or replace one,
and it can read options the player sets in the port. Mods are the same
`.nrm` files the other N64 recompilations use, built with the same tools.
A mod built from this template needs Snap64 Recomp 1.0.9 or later.

## What is here

* `src/mod_example.c` -- the example: a hook on the game's scene set-up that
  writes a line to the port's log, behind an option.
* `mod.toml` -- the mod's manifest (id, name, version, the game it is for,
  its options) and the inputs the mod tool reads.
* `Makefile`, `mod.ld` -- the MIPS build, with clang and lld.
* `include/` -- the modding headers: `modding.h` (the hook and patch
  macros), `recomputils.h` (printing and memory), `recompconfig.h` (reading
  the mod's options), `recompdata.h` (the hashmaps, hashsets and slotmaps a
  mod keeps between calls, held by the port). The other recompilations'
  `recompui.h` (menus a mod draws) is not here: the port does not provide
  those functions, and a mod that imports them does not load.
* `pokemonsnap/` -- the game's decompilation, as a submodule, for its headers
  and its function and variable names. `Snap64RecompSyms/` -- the symbol
  files the mod tool resolves those names with, as a submodule.
* `thunderstore/` -- the mod's Thunderstore page (`README.md`), its
  changelog and a placeholder icon, and `tools/pack_thunderstore.py`, which
  packs them with the `.nrm` (see "Publishing").
* `.github/workflows/build.yml` -- builds and packs the example on every
  push, from a clean clone, the way the section below says to.

## Tools

* `clang` and `ld.lld` that can target MIPS, and `make`. On Debian or
  Ubuntu: `clang`, `lld`, `make`. The other recompilations' templates say,
  for Windows, LLVM 18 (19.1.0 does not handle MIPS correctly for this
  build) and make, for example through Chocolatey (`llvm --version 18.1.8`,
  `make`); and for macOS, Homebrew's `llvm` and `make`, with
  `CC=/opt/homebrew/opt/llvm/bin/clang LD=/opt/homebrew/opt/llvm/bin/ld.lld`
  passed to make, because Apple's clang has no MIPS target. I build on
  Ubuntu and have not run the Windows or the macOS lines.
* `RecompModTool`, from [N64Recomp](https://github.com/N64Recomp/N64Recomp).
  Built from source at the commit the port itself is built against:

      git clone --recurse-submodules https://github.com/N64Recomp/N64Recomp
      cd N64Recomp
      git checkout ffb39cdad1da5de07eaaa48bd1db4a89a7986771
      git submodule update --init --recursive
      cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
      cmake --build build --target RecompModTool

  N64Recomp also publishes binaries for Windows and Linux (the
  `mod-tool-release` tag, May 2025). I have read that version's source and
  not run the binary: it reads every key this template's `mod.toml` uses,
  and it is older than optional dependencies, so a mod that declares one
  needs the tool built from source.
* On Linux and macOS the mod tool calls `zip` to write the `.nrm`, and says
  only `Failed to run "zip"` when it is missing: install it (`zip` on Debian
  or Ubuntu).

## Building

    git clone --recurse-submodules https://github.com/JackandBeans/Snap64RecompModTemplate
    cd Snap64RecompModTemplate
    make
    RecompModTool mod.toml build

`build/snap64_recomp_mod_template.nrm` is the mod. The decompilation is only
read for its headers and needs no build of its own.

## Installing it

Put the `.nrm` in the `mods/` folder next to `Snap64Recomp.exe` (or the
Linux binary; on a Mac, the `mods/` folder in
`~/Library/Application Support/Snap64 Recomp/`) and start the port. From 1.1.0 the port also takes the `.nrm`,
or the Thunderstore zip, dropped on its window, and unpacks a zip left in
`mods/`; either way the mod loads at the next start. A mod is turned on the first time the port
finds it; the log, `snap64.log`, names it as it opens and loads it, and the
example writes its line each time the game sets up a scene. The port's Mods
page (Options > Mods; Esc, or Select on a pad, opens the Options anywhere)
lists the mod with its version and author, turns it off or on, opens its
options and changes the load order. A change there takes effect the next
time the game starts, and `mods.json` beside the executable records it.

## Writing a mod

Hook a game function by name with `RECOMP_HOOK("name")` to run before it,
`RECOMP_HOOK_RETURN("name")` to run after it (the `recomphook_get_return_*`
functions read what it returned), or replace it with `RECOMP_PATCH` on a
function of the same name and signature. The names are the decompilation's:
`pokemonsnap/include/functions.h` and the sources under `pokemonsnap/src`,
and `Snap64RecompSyms/pokemonsnap.us.syms.toml` lists every function the
tool knows. Game variables are named too (`pokemonsnap.us.datasyms.toml`);
declare one `extern` with the decompilation's own type, exactly -- a
variable declared wider than it is reads and writes its neighbours -- and
use it. The game's headers (`common.h`, `sys/om.h` and the rest) include
as they are.

Options go in `mod.toml` under `[[manifest.config_options]]` and are read
with the functions in `recompconfig.h`. `recomp_printf` writes to the port's
log, `snap64.log`. `recompdata.h` gives a mod hashmaps, hashsets and
slotmaps that live for the run; the example keeps a set in one.

Two things the port does that a mod meets:

* **The port replaces some of the game's functions itself** (the sources
  under `patches/src` in the port's repository: the Options screen, the
  pause menu, the fade and a few more). A mod that replaces one of those
  with `RECOMP_PATCH` does not load, and the port says which function it
  was. `RECOMP_FORCE_PATCH` replaces it all the same, and takes the port's
  own change to that function away with it. A few more functions are
  wrapped by the port rather than replaced (the effect system's particle
  draw, the Pokémon add routines and a handful more, listed in the port's
  `tools/hook_funcs.py`); a hook on one of those still runs, on the port's
  wrapper. A hook (`RECOMP_HOOK`, `RECOMP_HOOK_RETURN`) on a function the
  port replaces works from 1.1.0.
* **At 1.0.9 three kinds of hook failed**: a hook on a function that calls
  the game's `memcpy`, on a function the port replaces, and on a function
  that waits a frame (`ohWait`, which most of the game's processes do; the
  game stopped when the process ended). 1.1.0 fixes all three. A mod with
  such a hook should ask for 1.1.0 in `minimum_recomp_version`.
* **`minimum_recomp_version` is checked against the port's own version.**
  1.0.9 is the first release that provides `recomp_printf` and the
  collections, so it is the lowest that makes sense here; a mod that asks
  for a release newer than the player's is refused with a message that
  names the version it wants.

## Publishing

Thunderstore is where the other N64 recompilations list their mods. A
Thunderstore package is a zip with a `manifest.json`, a `README.md` (the
package's page) and a 256x256 `icon.png` at its root, beside the mod.

1. Edit `thunderstore/README.md` and `thunderstore/CHANGELOG.md`, and
   replace `thunderstore/icon.png` (the placeholder is the port's film
   canister with a plus).
2. Build the mod, then run

       python tools/pack_thunderstore.py --team YourTeam --website https://github.com/you/your-mod

   The zip lands in `dist/`, named `YourTeam-Name-1.0.0.zip`: the package's
   name is `display_name` with spaces as underscores, its description
   `short_description` (Thunderstore takes 250 characters), and its version
   the mod's `version`.
3. Upload it at <https://thunderstore.io/package/create/> under your team.

Snap64 Recomp has no Thunderstore community yet; until it has, a GitHub
release carrying the `.nrm` and the zip does the same job. Mod managers do
not support the port, so a package's page should tell players to use
Manual Download, as the other recompilations' pages do. The port's Mods page
shows `short_description` on one line of about 45 characters, so a short one
reads whole there.

## What has been checked

From a clean clone, on Ubuntu 24.04 under WSL with clang and lld 18.1.3 and
a RecompModTool built from N64Recomp `ffb39cd`: the example builds and
packs, and the released 1.0.9 Windows executable loads it, turned on at
first sight, and writes its line at each scene. A second mod, which is not
in this repository, exercised the rest against the same executable: the
game's headers from the unbuilt decompilation checkout, a game variable by
name, a hook after a function reading its return value, a function
replaced, the replacement of a function the port itself replaces (refused,
then forced), and a manifest asking for a newer port (refused, with the
message). Not checked: the Windows and macOS tool lines above, the published
RecompModTool binary, native libraries, and dependencies between mods.

## Licence

This template is GPLv3, like the port. `modding.h`, `recomputils.h` and
`recompconfig.h` are the files of Zelda64Recomp's
[MMRecompModTemplate](https://github.com/Zelda64Recomp/MMRecompModTemplate),
unchanged, and the `Makefile` and `mod.ld` are adapted from its own; that
template is CC0. `recompdata.h` declares the same functions as the other
recompilations' header of that name, which the port provides. The
decompilation this reads headers from,
[ethteck/pokemonsnap](https://github.com/ethteck/pokemonsnap), carries no
licence file; it is checked out in place rather than copied, as the other
recompilations' templates do, and nothing of the game is in this repository.
