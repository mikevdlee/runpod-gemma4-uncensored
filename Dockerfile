# =============================================================================
# RunPod Serverless vLLM Worker — Gemma 4 31B Uncensored
# Based on: https://github.com/runpod-workers/worker-vllm
# Modified: Uses vLLM nightly (0.19+) for Gemma4ReasoningParser support
# =============================================================================

FROM nvidia/cuda:12.9.1-base-ubuntu22.04

RUN apt-get update -y \
    && apt-get install -y python3-pip git \
    && rm -rf /var/lib/apt/lists/*

RUN ldconfig /usr/local/cuda-12.9/compat/

# =============================================================================
# KEY CHANGE: Install vLLM nightly (includes Gemma4ReasoningParser)
# The official RunPod worker-vllm image uses vLLM 0.16.0 which does NOT
# include the gemma4 reasoning parser. We need vLLM 0.19+ for that.
# =============================================================================
RUN python3 -m pip install --upgrade pip && \
    pip install -U vllm --pre \
        --index-url https://pypi.org/simple \
        --extra-index-url https://wheels.vllm.ai/nightly && \
    pip install git+https://github.com/huggingface/transformers.git

# Install additional Python dependencies (after vLLM to avoid PyTorch conflicts)
COPY builder/requirements.txt /requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade -r /requirements.txt

# Setup for Option 2: Building the Image with the Model baked in
ARG MODEL_NAME=""
ARG TOKENIZER_NAME=""
ARG BASE_PATH="/runpod-volume"
ARG QUANTIZATION=""
ARG MODEL_REVISION=""
ARG TOKENIZER_REVISION=""

ENV MODEL_NAME=$MODEL_NAME \
    MODEL_REVISION=$MODEL_REVISION \
    TOKENIZER_NAME=$TOKENIZER_NAME \
    TOKENIZER_REVISION=$TOKENIZER_REVISION \
    BASE_PATH=$BASE_PATH \
    QUANTIZATION=$QUANTIZATION \
    HF_DATASETS_CACHE="${BASE_PATH}/huggingface-cache/datasets" \
    HUGGINGFACE_HUB_CACHE="${BASE_PATH}/huggingface-cache/hub" \
    HF_HOME="${BASE_PATH}/huggingface-cache/hub" \
    HF_HUB_ENABLE_HF_TRANSFER=0 \
    # Suppress Ray metrics agent warnings
    RAY_METRICS_EXPORT_ENABLED=0 \
    RAY_DISABLE_USAGE_STATS=1 \
    # Prevent rayon thread pool panic in containers
    TOKENIZERS_PARALLELISM=false \
    RAYON_NUM_THREADS=4

ENV PYTHONPATH="/:/vllm-workspace"

COPY src /src
RUN --mount=type=secret,id=HF_TOKEN,required=false \
    if [ -f /run/secrets/HF_TOKEN ]; then \
    export HF_TOKEN=$(cat /run/secrets/HF_TOKEN); \
    fi && \
    if [ -n "$MODEL_NAME" ]; then \
    python3 /src/download_model.py; \
    fi

# Start the handler
CMD ["python3", "/src/handler.py"]
