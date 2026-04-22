# RunPod Gemma 4 31B Uncensored — Serverless Worker

> 🚀 **Serverless LLM endpoint** voor [TrevorJS/gemma-4-31B-it-uncensored](https://huggingface.co/TrevorJS/gemma-4-31B-it-uncensored) op RunPod, met **reasoning/thinking** support via vLLM.

## Waarom dit project?

RunPod's officiele `worker-vllm` image (v2.14.0) draait op **vLLM 0.16.0**, dat de `gemma4` reasoning parser **niet** ondersteunt. Dit project bouwt een custom Docker image met **vLLM 0.19+** (nightly), waardoor de `Gemma4ReasoningParser` beschikbaar is.

## Features

- ✅ **Gemma 4 31B Uncensored** — abliterated model zonder refusal behavior
- ✅ **Reasoning/Thinking mode** — step-by-step denkproces via `REASONING_PARSER=gemma4`
- ✅ **OpenAI-compatible API** — direct bruikbaar met OpenAI SDK, TypingMind, etc.
- ✅ **Serverless** — pay-per-use, scale-to-zero wanneer je niet chat
- ✅ **Streaming** — real-time token streaming
- ✅ **GitHub Actions CI/CD** — automatische Docker image builds

## Quick Start

### 1. Fork & Clone
```bash
git clone https://github.com/mikevdlee/runpod-gemma4-uncensored.git
```

### 2. GitHub Actions bouwt automatisch
Na push naar `main` bouwt GitHub Actions het Docker image en pushed het naar:
```
ghcr.io/mikevdlee/runpod-gemma4-uncensored:latest
```

### 3. Deploy op RunPod
1. Ga naar [RunPod Serverless](https://console.runpod.io/serverless)
2. **New Endpoint** → Container Image: `ghcr.io/mikevdlee/runpod-gemma4-uncensored:latest`
3. **GPU:** A100 80GB
4. **Workers:** Min 0, Max 1
5. **Environment Variables** (kopieer uit `.env.example`):
   ```
   MODEL_NAME=TrevorJS/gemma-4-31B-it-uncensored
   DTYPE=bfloat16
   MAX_MODEL_LEN=8192
   GPU_MEMORY_UTILIZATION=0.92
   REASONING_PARSER=gemma4
   OPENAI_SERVED_MODEL_NAME_OVERRIDE=gemma-4-31b-uncensored
   ENABLE_CHUNKED_PREFILL=true
   MAX_NUM_SEQS=8
   ```
6. Optioneel: voeg `HF_TOKEN` toe als het model gated is
7. **Create**!

### 4. Koppel TypingMind
1. **Settings → Models → Add Custom Model**
2. **Endpoint:** `https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1/chat/completions`
3. **Model ID:** `gemma-4-31b-uncensored`
4. **API Key:** Je RunPod API Key

### 5. Test
```bash
pip install openai
set RUNPOD_API_KEY=your_key
set RUNPOD_ENDPOINT_ID=your_id
python scripts/test_endpoint.py
```

## API Gebruik

### Python (OpenAI SDK)
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_RUNPOD_API_KEY",
    base_url="https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/openai/v1"
)

response = client.chat.completions.create(
    model="gemma-4-31b-uncensored",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=256
)
print(response.choices[0].message.content)
```

### cURL
```bash
curl https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -d '{
    "model": "gemma-4-31b-uncensored",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 256
  }'
```

## GPU Vereisten

| GPU | VRAM | Geschikt? |
|:---|:---|:---|
| A100 80GB | 80 GB | ✅ Aanbevolen |
| H100 80GB | 80 GB | ✅ Beste performance |
| A100 40GB | 40 GB | ❌ Te weinig |
| RTX 4090 | 24 GB | ❌ Te weinig |

Het model is ~62 GB in bfloat16. Met KV-cache overhead is minimaal ~70-75 GB VRAM nodig.

## Kosten (Flex/Scale-to-Zero)

| Gebruik | GPU | Kosten |
|:---|:---|:---|
| 1 uur/dag | A100 80GB | ~$82/maand |
| 4 uur/dag | A100 80GB | ~$329/maand |
| Pay-per-request | A100 80GB | ~$0.00076/sec |

## Projectstructuur

```
├── Dockerfile                    # Custom vLLM nightly image
├── .github/workflows/build.yml  # Auto-build & push
├── src/
│   ├── handler.py               # RunPod serverless handler
│   ├── engine.py                # vLLM + OpenAI engine
│   ├── engine_args.py           # Engine configuration
│   ├── utils.py                 # Utilities
│   ├── constants.py             # Constants
│   ├── tokenizer.py             # Tokenizer wrapper
│   └── download_model.py        # Model download
├── builder/
│   └── requirements.txt         # Python dependencies
├── scripts/
│   └── test_endpoint.py         # Endpoint test script
├── .env.example                 # Environment variables template
└── README.md
```

## Credits

- Worker code based on [runpod-workers/worker-vllm](https://github.com/runpod-workers/worker-vllm) (MIT License)
- Model: [TrevorJS/gemma-4-31B-it-uncensored](https://huggingface.co/TrevorJS/gemma-4-31B-it-uncensored)
- Inference engine: [vLLM](https://github.com/vllm-project/vllm)

## License

MIT
