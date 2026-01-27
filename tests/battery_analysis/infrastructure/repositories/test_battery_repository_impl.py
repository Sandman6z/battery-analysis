# -*- coding: utf-8 -*-
"""
BatteryRepositoryImpl测试
"""

import pytest
from datetime import datetime
from battery_analysis.infrastructure.repositories.battery_repository_impl import BatteryRepositoryImpl
from battery_analysis.domain.entities.battery import Battery


class TestBatteryRepositoryImpl:
    """电池仓库实现测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建电池仓库实例
        self.repository = BatteryRepositoryImpl()
        
        # 创建测试电池对象
        self.test_battery_1 = Battery(
            serial_number="BAT-001",
            model_number="Model-A",
            manufacturer="Manufacturer A",
            production_date=datetime(2023, 1, 1),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.15
        )
        
        self.test_battery_2 = Battery(
            serial_number="BAT-002",
            model_number="Model-A",
            manufacturer="Manufacturer B",
            production_date=datetime(2023, 2, 1),
            battery_type="Ni-MH",
            nominal_voltage=1.2,
            nominal_capacity=2.5,
            max_voltage=1.4,
            min_voltage=1.0,
            max_current=3.0,
            weight=0.2
        )
        
        self.test_battery_3 = Battery(
            serial_number="BAT-003",
            model_number="Model-B",
            manufacturer="Manufacturer A",
            production_date=datetime(2023, 3, 1),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=3.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=6.0,
            weight=0.25
        )

    def test_save(self):
        """测试保存电池数据"""
        # 保存电池
        saved_battery = self.repository.save(self.test_battery_1)
        
        # 验证结果
        assert saved_battery is not None
        assert saved_battery.serial_number == "BAT-001"
        assert saved_battery.model_number == "Model-A"

    def test_find_by_serial_number(self):
        """测试根据序列号查找电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        
        # 查找电池
        found_battery = self.repository.find_by_serial_number("BAT-001")
        
        # 验证结果
        assert found_battery is not None
        assert found_battery.serial_number == "BAT-001"
        
        # 查找不存在的电池
        not_found_battery = self.repository.find_by_serial_number("BAT-999")
        assert not_found_battery is None

    def test_find_by_model_number(self):
        """测试根据型号查找电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        self.repository.save(self.test_battery_2)
        self.repository.save(self.test_battery_3)
        
        # 查找电池
        found_batteries = self.repository.find_by_model_number("Model-A")
        
        # 验证结果
        assert len(found_batteries) == 2
        assert all(battery.model_number == "Model-A" for battery in found_batteries)

    def test_find_by_manufacturer(self):
        """测试根据制造商查找电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        self.repository.save(self.test_battery_2)
        self.repository.save(self.test_battery_3)
        
        # 查找电池
        found_batteries = self.repository.find_by_manufacturer("Manufacturer A")
        
        # 验证结果
        assert len(found_batteries) == 2
        assert all(battery.manufacturer == "Manufacturer A" for battery in found_batteries)

    def test_find_by_battery_type(self):
        """测试根据电池类型查找电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        self.repository.save(self.test_battery_2)
        self.repository.save(self.test_battery_3)
        
        # 查找电池
        found_batteries = self.repository.find_by_battery_type("Li-ion")
        
        # 验证结果
        assert len(found_batteries) == 2
        assert all(battery.battery_type == "Li-ion" for battery in found_batteries)

    def test_find_by_production_date_range(self):
        """测试根据生产日期范围查找电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        self.repository.save(self.test_battery_2)
        self.repository.save(self.test_battery_3)
        
        # 查找电池
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 2, 28)
        found_batteries = self.repository.find_by_production_date_range(start_date, end_date)
        
        # 验证结果
        assert len(found_batteries) == 2
        assert all(start_date <= battery.production_date <= end_date for battery in found_batteries)

    def test_find_by_status(self):
        """测试根据状态查找电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        self.repository.save(self.test_battery_2)
        
        # 查找电池
        found_batteries = self.repository.find_by_status("active")
        
        # 验证结果
        assert len(found_batteries) == 2
        assert all(battery.status == "active" for battery in found_batteries)

    def test_find_all(self):
        """测试查找所有电池"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        self.repository.save(self.test_battery_2)
        self.repository.save(self.test_battery_3)
        
        # 查找所有电池
        all_batteries = self.repository.find_all()
        
        # 验证结果
        assert len(all_batteries) == 3
        
        # 测试分页
        paginated_batteries = self.repository.find_all(limit=2, offset=1)
        assert len(paginated_batteries) == 2

    def test_update(self):
        """测试更新电池信息"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        
        # 更新电池
        updated_battery = Battery(
            serial_number="BAT-001",
            model_number="Model-A",
            manufacturer="Updated Manufacturer",
            production_date=datetime(2023, 1, 1),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.15
        )
        
        # 执行更新
        result = self.repository.update(updated_battery)
        
        # 验证结果
        assert result is not None
        assert result.manufacturer == "Updated Manufacturer"
        
        # 验证数据库中的数据已更新
        found_battery = self.repository.find_by_serial_number("BAT-001")
        assert found_battery.manufacturer == "Updated Manufacturer"

    def test_delete(self):
        """测试删除电池信息"""
        # 保存电池
        self.repository.save(self.test_battery_1)
        
        # 验证电池存在
        assert self.repository.find_by_serial_number("BAT-001") is not None
        
        # 删除电池
        result = self.repository.delete("BAT-001")
        
        # 验证删除成功
        assert result is True
        
        # 验证电池不存在
        assert self.repository.find_by_serial_number("BAT-001") is None
        
        # 删除不存在的电池
        result = self.repository.delete("BAT-999")
        assert result is False

    def test_count(self):
        """测试统计电池数量"""
        # 验证初始数量
        assert self.repository.count() == 0
        
        # 保存电池
        self.repository.save(self.test_battery_1)
        assert self.repository.count() == 1
        
        self.repository.save(self.test_battery_2)
        assert self.repository.count() == 2
        
        # 删除电池
        self.repository.delete("BAT-001")
        assert self.repository.count() == 1
