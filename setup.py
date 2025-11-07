from setuptools import setup, find_packages
import os

# 读取README.md文件内容作为项目描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt文件内容作为项目依赖
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="battery-analysis",
    version="0.1.0",
    author="作者名称",
    author_email="作者邮箱",
    description="电池测试GUI应用程序",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="项目URL",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'battery-analysis=battery_analysis.main.main_window:main',
        ],
    },
)