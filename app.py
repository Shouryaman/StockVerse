"""Hugging Face Spaces entrypoint (Gradio SDK expects a global `demo`)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Must run before any `import gradio` (transitive imports use these at init time).
os.environ.setdefault("GRADIO_SERVER_NAME", "0.0.0.0")
_nop = "localhost,127.0.0.1,0.0.0.0,::1"
for _key in ("NO_PROXY", "no_proxy"):
    _existing = os.environ.get(_key, "").strip()
    os.environ[_key] = f"{_nop},{_existing}" if _existing else _nop

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stock_picker.gradio_ui import build_demo

demo = build_demo()
demo.queue()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860")))
    # Gradio probes localhost; in Docker/HF that often fails unless share=True or no_proxy is set.
    in_container = Path("/.dockerenv").exists()
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        inbrowser=False,
        share=in_container,
    )
