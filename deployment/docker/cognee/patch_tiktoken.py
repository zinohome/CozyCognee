"""Fix tiktoken KeyError for non-OpenAI embedding models (bge-m3, etc.)

Problem: Cognee's TikTokenTokenizer calls tiktoken.encoding_for_model(model)
which only recognizes OpenAI model names. Non-OpenAI models like bge-m3 raise
KeyError and crash the entire startup.

Fix: Wrap the encoding_for_model call in a try-except, falling back to
cl100k_base encoding for unknown models.
"""

import sys


def patch():
    # Direct file path — don't rely on import (venv may not be on sys.path during build)
    target = "/app/cognee/infrastructure/llm/tokenizer/TikToken/adapter.py"

    try:
        content = open(target).read()
    except FileNotFoundError:
        print(f"  {target}: not found, skipping")
        return True

    if "# PATCHED: fallback for non-OpenAI models" in content:
        print(f"  {target}: already patched")
        return True

    old = """        if model:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        else:
            # Use default if model not provided
            self.tokenizer = tiktoken.get_encoding("cl100k_base")"""

    new = """        if model:
            # PATCHED: fallback for non-OpenAI models (bge-m3, etc.)
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            # Use default if model not provided
            self.tokenizer = tiktoken.get_encoding("cl100k_base")"""

    if old not in content:
        print(f"  WARNING: target code not found in {target}")
        return False

    content = content.replace(old, new)
    open(target, "w").write(content)
    print(f"  {target}: patched (tiktoken fallback for non-OpenAI models)")
    return True


if __name__ == "__main__":
    if patch():
        print("TikToken fallback patch applied.")
    else:
        print("Patch failed.", file=sys.stderr)
        sys.exit(1)
