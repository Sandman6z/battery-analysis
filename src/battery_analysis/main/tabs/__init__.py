"""Main window tab widgets.

Each tab is a self-contained QWidget that occupies the full main area.
"""

from battery_analysis.main.tabs.battery_tab import BatteryAnalysisTab
from battery_analysis.main.tabs.ndax_tab import NdaxConverterTab

__all__ = ["BatteryAnalysisTab", "NdaxConverterTab"]
