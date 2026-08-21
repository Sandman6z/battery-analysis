"""statistics_utils 2D 批量统计契约锁测试"""
import numpy as np
import pytest

from battery_analysis.utils.writers.statistics_utils import (
    compute_list_cpt,
    compute_statistics,
)


def _sample_data():
    """B=3, C=2, V=2，等级平铺为 [c0v0, c0v1, c1v0, c1v1]"""
    return [
        [100, 0, 200, 50],   # 电池0（c0v1=0 被排除）
        [110, 90, 0, 60],    # 电池1（c1v0=0 被排除）
        [120, 95, 210, 0],   # 电池2（c1v1=0 被排除）
    ], 3, 2, 2


class TestComputeListCpt:
    def test_structure_and_collect(self):
        data, b, c, v = _sample_data()
        result = compute_list_cpt(data, b, c, v)
        assert result[0][0] == [100, 110, 120]
        assert result[0][1] == [90, 95]
        assert result[1][0] == [200, 210]
        assert result[1][1] == [50, 60]
        # 结构：len == V，每行 len == C
        assert len(result) == c and all(len(row) == v for row in result)


class TestComputeStatistics:
    def test_known_values(self):
        data, b, c, v = _sample_data()
        list_cpt = compute_list_cpt(data, b, c, v)
        stats = compute_statistics(list_cpt, c, v)

        assert stats['mean'][0][0] == pytest.approx(110.0)
        assert stats['med'][0][0] == pytest.approx(110.0)
        assert stats['std'][0][0] == pytest.approx(10.0)
        assert stats['min'][0][0] == pytest.approx(100.0)
        assert stats['max'][0][0] == pytest.approx(120.0)

        assert stats['mean'][0][1] == pytest.approx(92.5)
        assert stats['std'][0][1] == pytest.approx(np.std([90, 95], ddof=1))

        assert stats['mean'][1][0] == pytest.approx(205.0)
        assert stats['mean'][1][1] == pytest.approx(55.0)

        # 派生 ±Nσ
        assert stats['mp2s'][0][0] == pytest.approx(110.0 + 2 * 10.0)
        assert stats['mm3s'][0][0] == pytest.approx(110.0 - 3 * 10.0)

    def test_empty_cells_zero(self):
        list_cpt = [[[], []], [[], []]]
        stats = compute_statistics(list_cpt, 2, 2)
        assert stats['mean'] == [[0.0, 0.0], [0.0, 0.0]]
        assert stats['std'] == [[0.0, 0.0], [0.0, 0.0]]
        assert stats['min'] == [[0.0, 0.0], [0.0, 0.0]]
        assert stats['max'] == [[0.0, 0.0], [0.0, 0.0]]

    def test_matches_numeric_utils(self):
        """与逐 cell 调 numeric_utils 的结果一致（property 随机数据）"""
        from battery_analysis.utils import numeric_utils
        rng = np.random.default_rng(7)
        for _ in range(10):
            b, c, v = rng.integers(2, 6), rng.integers(1, 4), rng.integers(1, 4)
            data = rng.integers(0, 1000, size=(b, c * v)).tolist()
            list_cpt = compute_list_cpt(data, b, c, v)
            stats = compute_statistics(list_cpt, c, v)
            for ci in range(c):
                for vi in range(v):
                    cell = list_cpt[ci][vi]
                    assert stats['mean'][ci][vi] == pytest.approx(numeric_utils.np_mean(cell))
                    assert stats['med'][ci][vi] == pytest.approx(numeric_utils.np_med(cell))
                    assert stats['std'][ci][vi] == pytest.approx(numeric_utils.np_std(cell))
                    assert stats['min'][ci][vi] == pytest.approx(numeric_utils.np_min(cell))
                    assert stats['max'][ci][vi] == pytest.approx(numeric_utils.np_max(cell))
