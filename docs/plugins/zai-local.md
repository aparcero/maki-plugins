# zai-local

Included in the [maki-plugins collection](../../README.md). The implementation
is `lua/zai_local/init.lua`, loaded by `plugin/zai_local.lua`.

## Models and reasoning levels

`zai-local` offers GLM-5.4 (the default after login) and GLM-5.3 through the
OpenAI-compatible Z.ai Coding Plan endpoint. Both support `low`, `high`, and
`max` reasoning. The plugin sends those values directly because Maki 0.7.0's
built-in `zai` adapter converts `max` to `xhigh`. Maki's `adaptive` setting
selects `max`. An off setting, including a fresh configuration's default,
selects `low`. [Z.ai's GLM-5.4 FAQ](https://zcode.z.ai/en/docs/qa)

After installing the collection, start a new Maki process.
Authenticate the alias using `ZHIPU_API_KEY` from your secrets environment,
or run `maki auth login zai-local`
to save its key in Maki's credential store. The alias cannot reuse credentials
saved under the built-in `zai` slug. Never put the key in this repository.

Select `/model zai-local/glm-5.4` or `/model zai-local/glm-5.3` in Maki.
Use `/thinking low`, `/thinking high`, or `/thinking max` to set the effort.
You can also select the model at launch.

```sh
maki --model zai-local/glm-5.4
```

The alias has no Coding Plan quota display. Remove it when
the native adapter supports both models and their effort levels correctly.
`just check` verifies its outgoing requests against a loopback server
using dummy credentials, with no external model calls.

