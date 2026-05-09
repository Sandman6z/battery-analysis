# src/battery_analysis/utils/config_defaults.py
"""
配置默认值模块
首次运行时，如果 %APPDATA% 下没有 config.json，则从此模块创建初始数据。
"""

DEFAULT_CONFIG = {
    "version": 1,
    "battery": {
        "types": ["Coin Cell", "Pouch Cell"],
        "constructionMethods": ["Spiral Type", "Laminate Type"],
        "specifications": {
            "Coin Cell": ["CR2450", "CR2450YP", "CR2450PH", "CR2450D", "CR2450HE1", "CR2450HE4"],
            "Pouch Cell": ["CP224642A", "CF583083"]
        },
        "specificationMethods": ["1S1P", "1S2P", "2S1P"],
        "manufacturers": ["ATMT", "EVE", "Omnergy", "Nanfu", "Huiderui", "GP&LB", "HCB"],
        "rules": [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CR2450HE1/1S1P/600/550/380/1.0",
            "CR2450HE4/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0"
        ],
        "pulseCurrents": [30.0, 26.0, 15.0, 6.0],
        "cutOffVoltages": [2.6, 2.5, 2.4, 2.3, 2.25, 2.2, 2.1, 2.0, 1.8]
    },
    "test": {
        "locations": [
            "CT-4008Q (Qual.), BOE DT",
            "CT-4008Q (QA), BOE DT",
            "CT-4008Q (Qual.), PDI",
            "CT-4008Q (QA), BOE CQ",
            "CT-4008Q (QA), Liba M1",
            "CT-4008Q (QA), Jabil VN",
            "CT-4008Q (HWE), VG Fernitz"
        ],
        "testedBy": [
            "Hall", "Guoying Qi", "Zhaoxuan Zheng", "Xiaoe Wang",
            "Rachel Zhao", "Sandman Zhang", "Maiyue Zhang",
            "Howard Lin", "Kate Zhu", "Sy Tran", "Stefan"
        ],
        "equipment": {}
    },
    "window": {
        "width": 1200,
        "height": 800,
        "maximized": True
    }
}
