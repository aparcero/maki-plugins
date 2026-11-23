-- Maki 0.7.0 maps native Z.AI max to xhigh. Use the Coding Plan effort names.
maki.provider.register({
    slug = "zai-local",
    display_name = "Z.AI Coding Plan (local)",
    codec = "openai",
    base_url = "https://api.z.ai/api/coding/paas/v4",
    api_key_env = "ZHIPU_API_KEY",
    default_model = "glm-5.4",
    family = "glm",
    accepts_arbitrary_models = false,
    models = {
        {
            prefixes = { "glm-5.4", "glm-5.3" },
            tier = "strong",
            context_window = 1000000,
            max_output_tokens = 131072,
            supports_vision = false,
            requires_thinking = true,
            thinking_fields = {
                adaptive = { thinking = { type = "enabled" }, reasoning_effort = "max" },
                low = { thinking = { type = "enabled" }, reasoning_effort = "low" },
                high = { thinking = { type = "enabled" }, reasoning_effort = "high" },
                max = { thinking = { type = "enabled" }, reasoning_effort = "max" },
            },
        },
    },
    openai = { include_stream_usage = false },
})
