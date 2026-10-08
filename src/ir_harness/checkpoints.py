"""The five checkpoints of ``agent/checkpoint_workflow.md``.

Gates name the checkpoint to return to when they fail; correction signals name the
checkpoint a piece of feedback sends the agent back to.
"""

from __future__ import annotations

CHECKPOINTS: dict[int, str] = {
    1: "Task Understanding",
    2: "Sample Pool",
    3: "Classification Definitions",
    4: "Style Samples",
    5: "Draft And Visualize",
}
