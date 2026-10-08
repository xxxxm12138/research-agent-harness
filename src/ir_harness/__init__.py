"""ir_harness — an investment-research agent harness.

The markdown in ``agent/`` and ``skills/`` is the human-readable source of truth.
This package turns the parts that must not depend on the model's self-discipline
(routing, workspace assembly, point-in-time freezing, provenance labels, process
gates, rubric scoring, correction signals) into deterministic, testable code.
"""

__version__ = "0.1.0"
