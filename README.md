# maki-plugins

A collection of plugins for [Maki](https://maki.sh), installed as one Lua
package. Each integration has its own entry file, module namespace, and
documentation in this repository.

| Plugin | Purpose |
| --- | --- |
| [Herdr](docs/plugins/herdr.md) | Report agent status to Herdr, discover peers, exchange messages, and start or close agents |
| [ast-grep](docs/plugins/ast-grep.md) | Search, preview/apply structural rewrites, and inspect syntax trees |
| [zai-local](docs/plugins/zai-local.md) | Use GLM-5.3 and GLM-5.4 with Z.ai Coding Plan reasoning levels |

## Install

Requires Maki 0.7.0+. The ast-grep tools also need `ast-grep` on PATH
(or `ASTGREP_BIN`). Add the collection to your global Maki `init.lua`:

```lua
maki.pack.add({
  { src = "https://github.com/aparcero/maki-plugins" },
})
```

Maki shows the install prompt before the UI starts, then records the resolved
commit in `pack-lock.json`. Commit that file to pin the revision on other
machines. Permission requests in `plugin.toml` are approved separately.

All plugins ship and update together. Each plugin controls when its integration
activates; Herdr activates only inside a Herdr-managed pane. The ast-grep tools
and zai-local provider register at startup. Selecting a model and supplying
credentials remain user configuration.

[Harness](https://github.com/aparcero/harness) manages personal startup settings
and declares this package. This repository owns plugin behavior and tests;
it does not depend on a Harness checkout.

### Migrating from herdr.maki

Replace the old `maki.pack.add` entry with the one above, rather than adding a
second entry. Restart Maki to install the renamed package and approve its
permissions. Maki associates approvals with the package name and source, so the
new name requires a new approval. The Herdr tool and `/herdr` command keep their
existing names.

### Migrating from Harness's local extensions

Update Harness and apply `harness setup maki --only settings` after this
collection revision is available from Git. Its startup settings select this
package and stop requiring the local `ast_grep` and `zai_local` modules.
Restart Maki and accept package installation and permissions.
If the collection is already installed, run `/packupdate maki-plugins` to move
its locked revision to one containing the new extensions.

For manually managed configurations, remove `require("ast_grep")` and
`require("zai_local")` when adding the package. A custom ast-grep setup call
also needs to move to a [package loader](docs/plugins/ast-grep.md#configuration).
Previously installed `lua/ast_grep.lua` and `lua/zai_local.lua` can remain on
disk: they do not load automatically, and the package uses its own modules.
Harness leaves those files untouched, including local edits. Keep your existing
provider credentials, model selection, lockfile, and other personal state.

## Layout

```text
plugin/
  ast_grep.lua          ast-grep entry point
  herdr.lua             Herdr entry point
  zai_local.lua         zai-local entry point
lua/
  ast_grep/             Structural search and rewrite implementation
  herdr/                Herdr modules
  zai_local/            Provider declaration
docs/
  plugins/              Per-plugin usage and design
tests/                  Maki integration tests with loopback model fixtures
plugin.toml             Permissions requested by the collection
README.md               Plugin catalog and package instructions
```

Maki loads the `plugin/*.lua` entry files and resolves modules under `lua/`.
The entry files share a package environment. This follows Maki's native package
layout while keeping each integration's code in its own namespace.

## Permissions

Permissions apply to the whole collection:

| Permission | Used for |
| --- | --- |
| `env` | Reading Herdr variables, `ASTGREP_BIN`, and `ZHIPU_API_KEY` |
| `run` | Calling the `herdr` and `ast-grep` CLIs |
| `fs_read` | Reading `<cwd>/.agents/agent_config.json` for configured agent starts |
| `net` | Z.ai provider requests, restricted to `api.z.ai` |

The manifest declares the `zai-local` provider. It requests no Lua `fs_write`
permission; ast-grep applies rewrites through its subprocess, subject to Maki's
tool permissions and plan-mode checks.

## Adding a plugin

1. Add a small `plugin/<name>.lua` entry file and keep its implementation in
   `lua/<name>/`, using `require("<name>.<module>")` for its modules.
2. Keep plugins independent. Use local variables, a distinct module namespace,
   and unique tool and command names. An integration that requires a particular
   environment should return early when that environment is absent.
3. Document setup, behavior, and limitations in `docs/plugins/<name>.md`, then
   add it to the catalog above.
4. Declare any additional permissions in the shared `plugin.toml` and explain
   their use here. Package revisions and releases cover the whole collection.

Keep user configuration, runtime state, and credentials outside this checkout.

## Development

Edit the installed package's files, then run `/reload` in Maki to rebuild the
plugin host. Edits in a separate checkout must first reach the installed copy.
For the Herdr integration, follow its [verification steps](docs/plugins/herdr.md#verify-it).

Run `just check` for the ast-grep and zai-local regression suites. They require
Python (`python3` on Unix, `python` on Windows), Maki 0.7.0+, and ast-grep.
Tests install this checkout's package files into temporary Maki data directories
and use a scripted loopback model with dummy credentials. No Git download,
external model call, or live configuration change is needed. An existing
`~/.maki` is rejected because it would override the isolated configuration.

See Maki's [package documentation](https://maki.sh/docs/packages/) for package
loading, lockfiles, updates, and permissions.
