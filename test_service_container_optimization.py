#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务容器优化效果

测试内容：
1. 服务容器基本功能
2. 资源使用跟踪
3. 自动释放机制
4. 上下文管理器
"""

import logging
import time
from src.battery_analysis.main.services.service_container import (
    get_service_container, ServiceContext, MultiServiceContext
)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_service_container():
    """
    测试服务容器基本功能
    """
    logger.info("=== 测试服务容器基本功能 ===")
    
    container = get_service_container()
    
    # 测试服务注册
    class TestService:
        def __init__(self):
            self.name = "test_service"
        
        def get_name(self):
            return self.name
        
        def shutdown(self):
            logger.debug("TestService shutdown called")
    
    # 注册服务
    result = container.register("test", TestService)
    logger.info(f"注册服务结果: {result}")
    
    # 获取服务
    service = container.get("test")
    logger.info(f"获取服务结果: {service is not None}")
    if service:
        logger.info(f"服务名称: {service.get_name()}")
    
    # 测试服务信息
    info = container.get_service_info()
    logger.info(f"服务信息: {info}")
    
    # 测试资源使用信息
    usage = container.get_resource_usage()
    logger.info(f"资源使用信息: {usage}")

def test_resource_tracking():
    """
    测试资源使用跟踪
    """
    logger.info("\n=== 测试资源使用跟踪 ===")
    
    container = get_service_container()
    
    # 多次获取服务，测试访问计数
    for i in range(3):
        service = container.get("test")
        if service:
            logger.info(f"第 {i+1} 次获取服务")
        time.sleep(0.1)
    
    # 检查资源使用
    usage = container.get_resource_usage()
    logger.info(f"资源使用信息: {usage}")
    
    # 检查服务信息
    info = container.get_service_info()
    logger.info(f"服务信息: {info}")

def test_auto_release():
    """
    测试自动释放机制
    """
    logger.info("\n=== 测试自动释放机制 ===")
    
    container = get_service_container()
    
    # 获取初始实例数
    initial_instances = len(container._instances)
    logger.info(f"初始实例数: {initial_instances}")
    
    # 获取服务
    service = container.get("test")
    logger.info(f"获取服务后实例数: {len(container._instances)}")
    
    # 模拟空闲时间
    logger.info("模拟空闲时间...")
    time.sleep(2)  # 睡眠2秒
    
    # 释放未使用资源（使用1秒阈值）
    released = container.release_unused_resources(idle_time=1)
    logger.info(f"释放资源数量: {released}")
    logger.info(f"释放后实例数: {len(container._instances)}")
    
    # 再次获取服务
    service2 = container.get("test")
    logger.info(f"再次获取服务后实例数: {len(container._instances)}")
    logger.info(f"服务是否相同实例: {service is service2}")

def test_service_context():
    """
    测试服务上下文管理器
    """
    logger.info("\n=== 测试服务上下文管理器 ===")
    
    # 测试单个服务上下文
    logger.info("测试单个服务上下文...")
    with ServiceContext("test") as service:
        if service:
            logger.info(f"通过上下文管理器获取服务: {service.get_name()}")
        else:
            logger.warning("无法通过上下文管理器获取服务")
    
    # 测试多服务上下文
    logger.info("测试多服务上下文...")
    # 先注册另一个服务
    class AnotherService:
        def __init__(self):
            self.name = "another_service"
        
        def get_name(self):
            return self.name
    
    container = get_service_container()
    container.register("another", AnotherService)
    
    with MultiServiceContext(["test", "another"]) as services:
        test_service = services.get("test")
        another_service = services.get("another")
        
        if test_service:
            logger.info(f"通过多服务上下文获取测试服务: {test_service.get_name()}")
        if another_service:
            logger.info(f"通过多服务上下文获取另一个服务: {another_service.get_name()}")

def test_error_handling():
    """
    测试错误处理
    """
    logger.info("\n=== 测试错误处理 ===")
    
    # 测试获取不存在的服务
    container = get_service_container()
    service = container.get("non_existent")
    logger.info(f"获取不存在服务结果: {service is None}")
    
    # 测试上下文管理器获取不存在的服务
    logger.info("测试上下文管理器获取不存在的服务...")
    with ServiceContext("non_existent") as service:
        logger.info(f"上下文管理器获取不存在服务结果: {service is None}")

def main():
    """
    主测试函数
    """
    try:
        test_basic_service_container()
        test_resource_tracking()
        test_auto_release()
        test_service_context()
        test_error_handling()
        
        logger.info("\n=== 测试完成 ===")
        
        # 最终清理
        container = get_service_container()
        container.unregister("test")
        container.unregister("another")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    main()
