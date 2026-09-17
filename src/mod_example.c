#include "modding.h"
#include "recomputils.h"
#include "recompconfig.h"

// The game's own scene set-up, omSetupScene, runs every time a scene is
// built: the title, Professor Oak's lab, each course. A hook runs before the
// hooked function, with nothing of it changed; RECOMP_HOOK_RETURN runs after
// it, and RECOMP_PATCH replaces a function outright with one of the same
// name (its body then comes from the decompilation, changed as you like).
//
// Option ids are the ones in mod.toml; a Bool reads back as 0 or 1, an Enum
// as the index of the chosen option, a Number through the double getter.
RECOMP_HOOK("omSetupScene") void on_scene_setup(void) {
    if (recomp_get_config_u32("greeting") != 0) {
        recomp_printf("[mod template] a scene is being set up\n");
    }
}
