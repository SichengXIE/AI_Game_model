# Model Provider Interface v0.1

The product must let users choose their own model provider. The backend should treat models as a configurable service, not as a hard-coded vendor.

## 1. Scope

v0.1 supports one common API style:

```text
openai_chat_completions
```

This covers OpenAI-compatible chat completions endpoints from:

1. OpenAI
2. Google Gemini OpenAI compatibility
3. Qwen / DashScope OpenAI-compatible mode
4. Doubao / Volcengine Ark OpenAI-compatible mode
5. User-defined OpenAI-compatible gateways

The internal product contract stays the same: provider output must be parsed and validated as `Asset Spec v0.1`.

v0.1 also includes `local-demo`, a deterministic built-in provider for Web MVP demos and regression tests. It does not call an external model and should not be used as a replacement for real user-selected providers.

## 2. Configuration

Provider configuration is defined by:

```text
schemas/model-provider.schema.json
```

Example configuration:

```text
examples/model-providers.example.json
```

Secrets are never stored in provider config. Each provider points to an environment variable:

```json
{
  "id": "qwen-hk",
  "api_key_env": "DASHSCOPE_API_KEY"
}
```

The backend reads the key from the server environment at request time.

## 3. Provider Fields

Required fields:

1. `id`: stable provider identifier
2. `display_name`: user-facing name
3. `api_style`: currently `openai_chat_completions`
4. `base_url`: provider base URL
5. `api_key_env`: environment variable containing the API key
6. `default_model`: model used when the user does not override it
7. `enabled`: whether the provider is selectable

Optional fields:

1. `supports_json_schema`
2. `supports_streaming`
3. `timeout_seconds`
4. `extra_headers`
5. `extra_body`
6. `notes`

## 4. Default Providers

### Local Demo

`local-demo` is the default provider for the first Web MVP because it lets the full browser flow run without API keys:

```text
prompt -> local template response -> Asset Spec validation -> Package Builder -> zip download
```

The provider returns a valid station Asset Spec based on the repository example and applies small deterministic variants for modern, compact/suburban, and airport-like prompts.

### Gemini

Google documents an OpenAI-compatible Gemini endpoint. The default config uses:

```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

Set the key with:

```powershell
$env:GEMINI_API_KEY = "..."
```

### Qwen / DashScope

Alibaba Cloud Model Studio documents OpenAI-compatible Qwen access and lists regional endpoints. For a Hong Kong server, the default config uses:

```text
https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1
```

Set the key with:

```powershell
$env:DASHSCOPE_API_KEY = "..."
```

### Doubao / Volcengine Ark

Volcengine documents OpenAI-compatible usage by changing `base_url`, `model`, and `api_key`. The default config uses:

```text
https://ark.cn-beijing.volces.com/api/v3
```

Set the key with:

```powershell
$env:ARK_API_KEY = "..."
```

For Ark custom endpoints, users may replace `default_model` with their endpoint ID. Coding Plan users may choose:

```text
https://ark.cn-beijing.volces.com/api/coding/v3
```

## 5. Backend Contract

The backend exposes provider selection as a normal request parameter:

```json
{
  "provider_id": "qwen-hk",
  "model": "qwen-plus-latest",
  "prompt": "我想做一个港铁风格的换乘站"
}
```

The model adapter must return text. The next stage must parse that text as JSON and validate it against:

```text
schemas/asset-spec.schema.json
```

If validation fails, the backend should return a structured error and optionally ask the model for one repair attempt.

## 6. Implementation

The initial Python adapter lives in:

```text
backend/model_providers/
```

Important entry points:

1. `load_provider_catalog()`
2. `OpenAICompatibleClient`
3. `build_asset_spec_request()`
4. `generate_asset_spec_json()`

The adapter uses standard-library HTTP calls for now. It can later be replaced with the official OpenAI SDK if we want streaming, retries, tracing, or richer provider-specific options.

## 7. Safety Rules

1. Never store API keys in Git.
2. Never send provider keys to the browser.
3. Keep provider configs editable by users, but validate them with the schema before enabling.
4. Treat all provider output as untrusted until it passes `Asset Spec` validation.
5. Keep a provider-specific `extra_body` escape hatch for thinking controls or vendor-specific fields.

## 8. Sources

1. Google Gemini OpenAI compatibility: https://ai.google.dev/gemini-api/docs/openai
2. Alibaba Cloud Model Studio OpenAI-compatible Qwen: https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope
3. Volcengine OpenAI SDK compatibility: https://www.volcengine.com/docs/6492/2192012
4. Volcengine Ark online inference: https://www.volcengine.com/docs/82379/2121998
