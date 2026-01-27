import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.controllers.visualizer_controller import VisualizerController


class TestVisualizerController:
    def setup_method(self):
        self.controller = VisualizerController()

    def test_create_chart(self):
        chart_type = "line"
        data = {
            "x": [1, 2, 3],
            "y": [4.2, 4.1, 4.0]
        }
        with patch('battery_analysis.main.controllers.visualizer_controller.VisualizationManager') as mock_visualization_manager:
            mock_instance = Mock()
            mock_visualization_manager.return_value = mock_instance
            mock_instance.create_chart.return_value = {"chart": "created"}
            result = self.controller.create_chart(chart_type, data)
            assert result is not None

    def test_update_chart(self):
        chart_id = "chart1"
        data = {
            "x": [1, 2, 3, 4],
            "y": [4.2, 4.1, 4.0, 3.9]
        }
        with patch('battery_analysis.main.controllers.visualizer_controller.VisualizationManager') as mock_visualization_manager:
            mock_instance = Mock()
            mock_visualization_manager.return_value = mock_instance
            mock_instance.update_chart.return_value = {"chart": "updated"}
            result = self.controller.update_chart(chart_id, data)
            assert result is not None

    def test_export_chart(self):
        chart_id = "chart1"
        file_path = "chart.png"
        with patch('battery_analysis.main.controllers.visualizer_controller.VisualizationManager') as mock_visualization_manager:
            mock_instance = Mock()
            mock_visualization_manager.return_value = mock_instance
            mock_instance.export_chart.return_value = True
            result = self.controller.export_chart(chart_id, file_path)
            assert result is True