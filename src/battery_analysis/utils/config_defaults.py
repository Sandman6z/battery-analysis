# src/battery_analysis/utils/config_defaults.py
"""
配置默认值模块
首次运行时，如果 %APPDATA% 下没有 config.json，则从此模块创建初始数据。
"""

from battery_analysis.utils.battery_classifier import derive_specifications

DEFAULT_CONFIG = {
    "version": 1,
    "battery": {
        "types": ["Coin Cell", "Pouch Cell"],
        "constructionMethods": ["Spiral Type", "Laminate Type"],
        "specifications": {},  # 从 rules 自动派生，启动时由配置对话框填充
        "specificationMethods": ["1S1P", "1S2P", "2S1P"],
        "manufacturers": ["ATMT", "EVE", "Omnergy", "Nanfu", "Huiderui", "GP&LB", "HCB"],
        "rules": [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CR2450HE1/1S1P/600/550/380/1.0",
            "CR2450HE4/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0",
            "CP305050/1S1P/2000/2000/80%/1.0"
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
        "equipment": {
            "BOEDT.Qual": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
                    "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
                    "btsda": "BTSDA 8.0.0.502(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.36T",
                    "serialNumber": "T2302-370530",
                    "firmwareVersion": "4S_2.15.6.0_20220517_095718",
                    "deviceType": "BTS82"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
                    "hardwareVersion": "B01-BTS-XWJ-M-7.B.19QSn",
                    "firmwareVersion": "M04310100_220818_094651_FD4F1"
                }
            },
            "BOEDT.QA": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
                    "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
                    "btsda": "BTSDA 8.0.0.502(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.38T",
                    "serialNumber": "T2308-409388, T2308-409389",
                    "firmwareVersion": "4S_4.2.5.0_20230308_185745",
                    "deviceType": "BTS83"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
                    "hardwareVersion": "B01-BTS-XWJ-7.B.19QSn, B01-BTS-XWJ-M-7.B.18QMn",
                    "firmwareVersion": "M04310100_220818_094651_FD4F1"
                }
            },
            "PDI.Qual": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
                    "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
                    "btsda": "BTSDA 8.0.0.502(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.38T",
                    "serialNumber": "T2308-409382, T2308-409383",
                    "firmwareVersion": "4S_4.2.5.0_20230308_185745",
                    "deviceType": "BTS83"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
                    "hardwareVersion": "B01-BTS-XWJ-7.B.19QSn, B01-BTS-XWJ-7.B.18QMn",
                    "firmwareVersion": "M04310100_220818_094651_FD4F1, M043106_221114_111541_FD4F1"
                }
            },
            "BOECQ.QA": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
                    "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
                    "btsda": "BTSDA 8.0.0.502(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.38T",
                    "serialNumber": "T2308-409384, T2308-409385",
                    "firmwareVersion": "4S_4.2.5.0_20230308_185745",
                    "deviceType": "BTS83"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
                    "hardwareVersion": "B01-BTS-XWJ-7.B.19QMn, B01-BTS-XWJ-7.B.19QMn",
                    "firmwareVersion": "M04310100_220818_094651_FD4F1, M043106_221114_111541_FD4F1"
                }
            },
            "LibaM1.QA": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-0.0.0.000 (2023.05.31)",
                    "btsClient": "BTS Client 0.0.0.000(2023.05.31)",
                    "btsda": "BTSDA 0.0.0.000(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.36T",
                    "serialNumber": "T2302-000000",
                    "firmwareVersion": "4S_2.15.6.0_20220517_095718",
                    "deviceType": "BTS00"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
                    "hardwareVersion": "B01-BTS-XWJ-M-7.B.19QSn",
                    "firmwareVersion": "M04310100_220818_094651_FD4F1"
                }
            },
            "JabilVN.QA": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
                    "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
                    "btsda": "BTSDA 8.0.0.502(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.38T",
                    "serialNumber": "T2308-409386, T2308-409387",
                    "firmwareVersion": "4S_4.2.5.0_20230308_185745",
                    "deviceType": "BTS83"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
                    "hardwareVersion": "B01-BTS-XWJ-7.B.19QMn, B01-BTS-XWJ-7.B.19QMn",
                    "firmwareVersion": "M04310100_220818_094651_FD4F1, M043106_221114_111541_FD4F1"
                }
            },
            "VGFernitz.HWE": {
                "testEquipment": "NEWARE Battery Testing System CT-4008Q",
                "softwareVersions": {
                    "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
                    "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
                    "btsda": "BTSDA 8.0.0.502(2023.05.31)"
                },
                "middleMachines": {
                    "model": "CT-ZWJ-4'S-T-1U",
                    "hardwareVersion": "B01-BTS-ZWJ-4.36T, B01-BTS-ZWJ-4.38T",
                    "serialNumber": "T2208-339343, T2305-397958, T2305-397957",
                    "firmwareVersion": "4S_2.15.6.0_20220517_095718, 4S_4.2.5.0_20230308_185745",
                    "deviceType": "BTS82, BTS83"
                },
                "testUnits": {
                    "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6V-S1",
                    "hardwareVersion": "B01-BTS-XWJ-7.B.07QS, B01-BTS-XWJ-7.B.13QMn",
                    "firmwareVersion": "M04070700_211028_091905_EC4F1, M04070701_211112_105243_FD4F1"
                }
            }
        }
    },
    "window": {
        "width": 1200,
        "height": 800,
        "maximized": True
    }
}

# Specifications 从 rules 自动派生（单一来源：battery_classifier.derive_specifications）
DEFAULT_CONFIG["battery"]["specifications"] = derive_specifications(DEFAULT_CONFIG["battery"]["rules"])
