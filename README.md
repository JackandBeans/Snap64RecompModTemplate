# Snap64 Recomp mod template

A working example of a mod for [Snap64 Recomp](https://github.com/JackandBeans/Snap64Recomp),
and the files to start one of your own. A mod is code that runs inside the
recompiled game: it can hook a game function, run after one, or replace one,
and it can read options the player sets in the port. Mods are the same
`.nrm` files the other N64 recompilations use, built with the same tools.

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
  those functions yet, and a mod that imports them does not load.
* `pokemonsnap/` -- the game's decompilation, as a submodule, for its headers
  and its function and variable names. `Snap64RecompSyms/` -- the symbol
  files the mod tool resolves those names with, as a submodule.

## Tools

* `clang` and `ld.lld` that can target MIPS, and `make`. On Windows,
  install LLVM 18 (19.1.0 does not handle MIPS correctly for this build) and
  make, for example through Chocolatey (`llvm --version 18.1.8`, `make`).
  On Debian or Ubuntu: `clang`, `lld`, `make`. On macOS: Homebrew's `llvm`
  and `make`; Apple's clang has no MIPS target, so pass
  `CC=/opt/homebrew/opt/llvm/bin/clang LD=/opt/homebrew/opt/llvm/bin/ld.lld`
  to make.
* `RecompModTool`, from the [N64Recomp](https://github.com/N64Recomp/N64Recomp)
  releases (Windows and Linux binaries), or built from that repository.

## Building

    git clone --recurse-submodules https://github.com/JackandBeans/Snap64RecompModTemplate
    cd Snap64RecompModTemplate
    make
    RecompModTool mod.toml build

`build/snap64_recomp_mod_template.nrm` is the mod. Put it in the `mods/`
folder next to `Snap64Recomp.exe` (or the Linux binary) and start the port:
the log names it as it loads, and the mod menu, when the port has one, lists
it. Until then `mods.json` beside the folder says which mods are enabled.

## Writing a mod

Hook a game function by name with `RECOMP_HOOK("name")` to run before it,
`RECOMP_HOOK_RETURN("name")` to run after it, or replace it with
`RECOMP_PATCH` on a function of the same name and signature. The names are
the decompilation's: `pokemonsnap/include/functions.h` and the sources under
`pokemonsnap/src`, and `Snap64RecompSyms/pokemonsnap.us.syms.toml` lists
every function the tool knows. Game variables are named too
(`pokemonsnap.us.datasyms.toml`); declare one `extern` with the
decompilation's type and use it.

Options go in `mod.toml` under `[[manifest.config_options]]` and are read
with the functions in `recompconfig.h`. `recomp_printf` writes to the port's
log, `snap64.log`. `recompdata.h` gives a mod hashmaps, hashsets and
slotmaps that live for the run; the example keeps a set of the scenes it
has seen in one.

A few of the game's functions are already wrapped by the port itself (the
ride camera's two processes, the effect system's particle draw, the
Pokémon add routines and a handful more, listed in the port's
`tools/hook_funcs.py`); a hook on one of those still runs, on the port's
wrapper.

## Licence

This template is GPLv3, like the port. The decompilation it reads headers
from, [ethteck/pokemonsnap](https://github.com/ethteck/pokemonsnap), carries
no licence file; it is checked out in place rather than copied, as the other
recompilations' templates do, and nothing of the game is in this repository.
