"""Single source of truth for chart colors.

Aligned to a WCAG-AA-compliant set against white. Used by both Plotly and
Chart.js backends so visual identity stays consistent.
"""
from __future__ import annotations

# Brand primary + accent — ~5:1 contrast on white
PRIMARY = "#1d4ed8"   # blue-700
ACCENT = "#0891b2"    # cyan-700
SUCCESS = "#16a34a"   # green-600
WARNING = "#d97706"   # amber-600
DANGER = "#dc2626"    # red-600
NEUTRAL = "#6b7280"   # gray-500

# Sequential / categorical sets used by tabs
NEW_USER_PALETTE = [PRIMARY, "#3b82f6", "#60a5fa", "#93c5fd"]
RETURNING_USER_PALETTE = [ACCENT, "#06b6d4", "#22d3ee", "#67e8f9"]
USER_TYPE_PALETTE = [PRIMARY, ACCENT]

CHART_CONFIG = {"displayModeBar": False}
