"""Fix LiteLLM UnsupportedParamsError for non-OpenAI embedding models.

Problem: LiteLLM's get_optional_params_embeddings() raises UnsupportedParamsError
when `dimensions` is passed for models using the openai/ provider prefix, even
when litellm.drop_params=True (the check happens before drop_params is evaluated).

Fix: Patch LiteLLMEmbeddingEngine to skip passing `dimensions` when the model
uses openai/ prefix with a non-OpenAI model (like bge-m3 via Ollama).
"""

import sys

TARGET = "/app/cognee/infrastructure/databases/vector/embeddings/LiteLLMEmbeddingEngine.py"


def patch():
    try:
        content = open(TARGET).read()
    except FileNotFoundError:
        print(f"  {TARGET}: not found, skipping")
        return True

    if "# PATCHED: skip dimensions" in content:
        print(f"  {TARGET}: already patched")
        return True

    old = """                    # Pass through target embedding dimensions when supported
                    if self.dimensions is not None:
                        embedding_kwargs["dimensions"] = self.dimensions"""

    new = """                    # PATCHED: skip dimensions for openai/ prefixed non-OpenAI models
                    # LiteLLM raises UnsupportedParamsError for dimensions with openai/ provider
                    if self.dimensions is not None and not self.model.startswith("openai/"):
                        embedding_kwargs["dimensions"] = self.dimensions"""

    if old not in content:
        print(f"  WARNING: target code not found in {TARGET}")
        return False

    content = content.replace(old, new)
    open(TARGET, "w").write(content)
    print(f"  {TARGET}: patched (skip dimensions for openai/ models)")
    return True


if __name__ == "__main__":
    if patch():
        print("LiteLLM dimensions patch applied.")
    else:
        print("Patch failed.", file=sys.stderr)
        sys.exit(1)
