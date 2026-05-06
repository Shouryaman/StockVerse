"""Interactive Gradio frontend for stock_picker without modifying core crew logic."""

from __future__ import annotations

import os
import socket
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SECTORS = [
    "Technology",
    "Healthcare",
    "Financial Services",
    "Energy",
    "Consumer Discretionary",
    "Industrials",
    "Communication Services",
]


@contextmanager
def _project_cwd():
    prev = Path.cwd()
    try:
        os.chdir(PROJECT_ROOT)
        yield
    finally:
        os.chdir(prev)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _pick_port(host: str, requested: int) -> int:
    for port in range(requested, requested + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError(f"No free port available from {requested} to {requested + 19}.")


def build_demo() -> gr.Blocks:
    """Build the Gradio UI (used by Hugging Face Spaces via root `app.py`)."""
    with gr.Blocks(title="Stock Picker Frontend") as demo:
        gr.Markdown("## Stock Picker\nRun the existing CrewAI stock picker interactively.")

        with gr.Row():
            sector = gr.Dropdown(SECTORS, value="Technology", label="Sector")
            custom_sector = gr.Textbox(label="Or custom sector", placeholder="e.g. Cybersecurity")

        run_btn = gr.Button("Run Stock Picker", variant="primary")

        selected_sector = gr.Textbox(label="Chosen sector")
        summary = gr.Textbox(label="Final summary", lines=12)
        decision = gr.Textbox(label="Decision report (output/decision.md)", lines=16)
        trending = gr.Textbox(label="Trending companies JSON", lines=10)
        research = gr.Textbox(label="Research report JSON", lines=12)

        run_btn.click(
            run_stock_picker,
            inputs=[sector, custom_sector],
            outputs=[selected_sector, summary, decision, trending, research],
        )

    return demo


def run_stock_picker(sector: str, custom_sector: str):
    from stock_picker.crew import StockPicker

    chosen_sector = (custom_sector or "").strip() or (sector or "Technology")
    if not chosen_sector:
        raise gr.Error("Please select or enter a sector.")

    inputs = {"sector": chosen_sector, "current_date": str(datetime.now())}

    try:
        with _project_cwd():
            result = StockPicker().crew().kickoff(inputs=inputs)
    except Exception as exc:
        raise gr.Error(f"Stock picker run failed: {exc}") from exc

    out_dir = PROJECT_ROOT / "output"
    trending = _read_text(out_dir / "trending_companies.json")
    research = _read_text(out_dir / "research_report.json")
    decision = _read_text(out_dir / "decision.md")
    summary = result.raw if hasattr(result, "raw") else str(result)
    return chosen_sector, summary, decision, trending, research


def main() -> None:
    host = os.getenv("STOCK_PICKER_UI_HOST", "127.0.0.1")
    requested_port = int(os.getenv("STOCK_PICKER_UI_PORT", "7861"))
    share = os.getenv("STOCK_PICKER_UI_SHARE", "false").lower() in {"1", "true", "yes"}
    port = _pick_port(host, requested_port)

    demo = build_demo()
    demo.queue()
    demo.launch(server_name=host, server_port=port, share=share)


if __name__ == "__main__":
    main()
