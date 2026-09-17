#include "modding.h"
#include "recomputils.h"
#include "recompconfig.h"
#include "recompdata.h"

// The game's own scene set-up, omSetupScene, runs every time a scene is
// built: the title, Professor Oak's lab, each course. A hook runs before the
// hooked function, with nothing of it changed; RECOMP_HOOK_RETURN runs after
// it, and RECOMP_PATCH replaces a function outright with one of the same
// name (its body then comes from the decompilation, changed as you like).
//
// Option ids are the ones in mod.toml; a Bool reads back as 0 or 1, an Enum
// as the index of the chosen option, a Number through the double getter.
//
// The set below is one of recompdata.h's collections: it lives on the
// host, for the whole run, and here it counts how many times the scene
// set-up has run and how many of those were the first of their kind (the
// key is the count itself, so every one is new; a real mod would key it by
// something of the scene's).

static U32HashsetHandle seen_scenes = 0;
static unsigned long scene_count = 0;

RECOMP_HOOK("omSetupScene") void on_scene_setup(void) {
    if (seen_scenes == 0) {
        seen_scenes = recomputil_create_u32_hashset();
    }
    scene_count++;
    int was_new = recomputil_u32_hashset_insert(seen_scenes, scene_count);
    if (recomp_get_config_u32("greeting") != 0) {
        recomp_printf("[mod template] a scene is being set up (number %lu, %s; %lu in the set)\n",
                      scene_count, was_new ? "new" : "seen", recomputil_u32_hashset_size(seen_scenes));
    }
}
