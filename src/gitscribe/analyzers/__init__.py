"""Analyzers that derive facts from Git history (deterministic, no LLM)."""

from gitscribe.analyzers.breaking import detect_breaking_changes
from gitscribe.analyzers.architecture import analyze_architecture_evolution
from gitscribe.analyzers.timeline import build_development_timeline
from gitscribe.analyzers.churn import compute_churn_report

__all__ = [
    "detect_breaking_changes",
    "analyze_architecture_evolution",
    "build_development_timeline",
    "compute_churn_report",
]
