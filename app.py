"""Hugging Face Spaces entrypoint (Gradio SDK expects a global `demo`)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stock_picker.gradio_ui import build_demo

demo = build_demo()
demo.queue()

if __name__ == "__main__":
    # Hugging Face Spaces often runs `python app.py`; without launch() the process exits 0 immediately.
    import os

    port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860")))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
