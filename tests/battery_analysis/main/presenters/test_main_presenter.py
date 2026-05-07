from unittest.mock import Mock
from battery_analysis.main.presenters.main_presenter import MainPresenter


class TestMainPresenter:
    def setup_method(self):
        self.view = Mock()
        self.presenter = MainPresenter(self.view)

    def test_initialization(self):
        assert self.presenter.view == self.view