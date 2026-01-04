# 代码重构计划

## 概述
- 分析日期: 2026-01-04 10:20:55
- 总文件数: 65
- 存在问题的文件数: 65
- 问题类型总数: 39
- 问题总数: 451

## 问题类型: attribute-defined-outside-init
### 问题信息
- 类型: warning
- 代码: W0201
- 描述: Attribute 'ide_mode' defined outside __init__
- 出现次数: 134
- 涉及文件数: 3

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 67, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'ide_mode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 76, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'container_mode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 85, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'production_mode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 83, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'chart_type_combo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 88, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'filter_checkbox' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 93, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'refresh_button' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 118, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'chart_title' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 193, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'data_info_label' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 200, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'zoom_in_button' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 201, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'zoom_out_button' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 202, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'reset_zoom_button' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 355, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'battery_names' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 24, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'centralwidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 31, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_BatteryConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 38, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 44, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 47, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 50, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 53, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 67, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 95, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 98, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 112, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'spinBox_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 131, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_2' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 136, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 139, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 142, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 145, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 159, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 203, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 206, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 220, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 239, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 242, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 256, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 275, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 280, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 283, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 286, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 289, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 303, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 353, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 356, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 370, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 419, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 422, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 436, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 441, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Method' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 490, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Type' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 542, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 547, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 550, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 553, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 556, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 570, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 589, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 592, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 601, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 619, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 622, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 636, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 659, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 671, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 678, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 681, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 695, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 719, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 733, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_10' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 740, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 743, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 757, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 799, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 806, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 809, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 823, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 870, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_Path' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 877, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_11' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 884, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 887, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 901, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 920, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 934, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_12' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 941, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 944, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 953, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 972, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 981, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 991, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollArea' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 995, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollAreaWidgetContents' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1003, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1005, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'tableWidget_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1093, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_RunButton' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1098, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1104, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_RunAndVersion' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1107, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1111, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_Run' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1153, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1163, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'progressBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1173, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1175, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1179, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1192, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1214, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'statusBar_BatteryAnalysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1217, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1220, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuFile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1222, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuEdit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1224, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuView' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1226, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuTools' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1228, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1231, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionNew' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1233, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1235, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1237, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_As' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1239, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExport_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1241, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1243, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUndo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1245, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRedo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1247, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCut' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1249, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCopy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1251, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPaste' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1253, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPreferences' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1255, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Toolbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1257, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Statusbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1259, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_In' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1261, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_Out' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1263, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionReset_Zoom' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1265, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCalculate_Battery' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1267, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAnalyze_Data' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1269, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionGenerate_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1271, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatch_Processing' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1273, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUser_Mannual' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1275, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOnline_Help' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1277, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAbout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1279, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatteryChartViewer' defined outside __init__
- 符号: attribute-defined-outside-init

## 问题类型: astroid-error
### 问题信息
- 类型: fatal
- 代码: F0002
- 描述: scripts\build.py: Fatal error while checking 'scripts\build.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-41.txt'.
- 出现次数: 38
- 涉及文件数: 38

### 详细问题列表
#### 文件: scripts\build.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\build.py: Fatal error while checking 'scripts\build.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-41.txt'.
- 符号: astroid-error

#### 文件: scripts\compile_translations.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\compile_translations.py: Fatal error while checking 'scripts\compile_translations.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-41.txt'.
- 符号: astroid-error

#### 文件: scripts\extract_translations.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\extract_translations.py: Fatal error while checking 'scripts\extract_translations.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-41.txt'.
- 符号: astroid-error

#### 文件: scripts\setup_i18n.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\setup_i18n.py: Fatal error while checking 'scripts\setup_i18n.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-42.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\chart\interfaces\ichart_manager.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\chart\interfaces\ichart_manager.py: Fatal error while checking 'src\battery_analysis\chart\interfaces\ichart_manager.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-42.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\data\interfaces\idataprocessor.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\data\interfaces\idataprocessor.py: Fatal error while checking 'src\battery_analysis\data\interfaces\idataprocessor.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-42.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\i18n\__init__.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\i18n\__init__.py: Fatal error while checking 'src\battery_analysis\i18n\__init__.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-42.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\i18n\language_manager.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\i18n\language_manager.py: Fatal error while checking 'src\battery_analysis\i18n\language_manager.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-42.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\i18n\preferences_dialog.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\i18n\preferences_dialog.py: Fatal error while checking 'src\battery_analysis\i18n\preferences_dialog.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-42.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\battery_chart_viewer.py: Fatal error while checking 'src\battery_analysis\main\battery_chart_viewer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-43.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\controllers\file_controller.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\controllers\file_controller.py: Fatal error while checking 'src\battery_analysis\main\controllers\file_controller.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-43.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\factories\visualizer_factory.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\factories\visualizer_factory.py: Fatal error while checking 'src\battery_analysis\main\factories\visualizer_factory.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\interfaces\ivisualizer.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\interfaces\ivisualizer.py: Fatal error while checking 'src\battery_analysis\main\interfaces\ivisualizer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\main_window.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\main_window.py: Fatal error while checking 'src\battery_analysis\main\main_window.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\application_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\application_service.py: Fatal error while checking 'src\battery_analysis\main\services\application_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\config_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\config_service.py: Fatal error while checking 'src\battery_analysis\main\services\config_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\config_service_interface.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\config_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\config_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\data_processing_service_interface.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\data_processing_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\data_processing_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-44.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\document_service_interface.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\document_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\document_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\environment_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\environment_service.py: Fatal error while checking 'src\battery_analysis\main\services\environment_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\event_bus.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\event_bus.py: Fatal error while checking 'src\battery_analysis\main\services\event_bus.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\file_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\file_service.py: Fatal error while checking 'src\battery_analysis\main\services\file_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\file_service_interface.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\file_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\file_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\i18n_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\i18n_service.py: Fatal error while checking 'src\battery_analysis\main\services\i18n_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\progress_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\progress_service.py: Fatal error while checking 'src\battery_analysis\main\services\progress_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\service_container.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\service_container.py: Fatal error while checking 'src\battery_analysis\main\services\service_container.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-40.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\validation_service.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\validation_service.py: Fatal error while checking 'src\battery_analysis\main\services\validation_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\main\services\validation_service_interface.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\validation_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\validation_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-45.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py: Fatal error while checking 'src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-46.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\ui\interfaces\iuiframework.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\interfaces\iuiframework.py: Fatal error while checking 'src\battery_analysis\ui\interfaces\iuiframework.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-46.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\ui\modern_battery_viewer.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\modern_battery_viewer.py: Fatal error while checking 'src\battery_analysis\ui\modern_battery_viewer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-46.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\modern_battery_viewer_refactored.py: Fatal error while checking 'src\battery_analysis\ui\modern_battery_viewer_refactored.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-46.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\ui\modern_theme.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\modern_theme.py: Fatal error while checking 'src\battery_analysis\ui\modern_theme.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-49.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\ui\styles\style_manager.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\styles\style_manager.py: Fatal error while checking 'src\battery_analysis\ui\styles\style_manager.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-49.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\utils\config_parser.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\config_parser.py: Fatal error while checking 'src\battery_analysis\utils\config_parser.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-50.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\utils\environment_utils.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\environment_utils.py: Fatal error while checking 'src\battery_analysis\utils\environment_utils.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-50.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\utils\file_writer.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\file_writer.py: Fatal error while checking 'src\battery_analysis\utils\file_writer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-40.txt'.
- 符号: astroid-error

#### 文件: src\battery_analysis\utils\version.py
- 位置: 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\version.py: Fatal error while checking 'src\battery_analysis\utils\version.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-20-51.txt'.
- 符号: astroid-error

## 问题类型: ungrouped-imports
### 问题信息
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 出现次数: 35
- 涉及文件数: 18

### 详细问题列表
#### 文件: scripts\compile_translations.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\compile_translations.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\compile_translations.py
- 位置: 行 11, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package subprocess are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\compile_translations.py
- 位置: 行 12, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\compile_translations.py
- 位置: 行 13, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\extract_translations.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\extract_translations.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\extract_translations.py
- 位置: 行 11, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package subprocess are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\extract_translations.py
- 位置: 行 12, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\extract_translations.py
- 位置: 行 13, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 文件: scripts\fix_logging_fstrings.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\__init__.py
- 位置: 行 3, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\i18n\language_manager.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\i18n\language_manager.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\i18n\language_manager.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\i18n\preferences_dialog.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 29, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 30, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 35, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\main_window.py
- 位置: 行 14, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\services\environment_service.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\services\file_service_interface.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package abc are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\services\i18n_service.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\services\validation_service.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\services\validation_service.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\main\services\validation_service_interface.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package abc are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_battery_viewer.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py
- 位置: 行 11, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 6, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

## 问题类型: missing-final-newline
### 问题信息
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 出现次数: 31
- 涉及文件数: 31

### 详细问题列表
#### 文件: scripts\build.py
- 位置: 行 720, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: scripts\compile_translations.py
- 位置: 行 263, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: scripts\extract_translations.py
- 位置: 行 345, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: scripts\po_translator.py
- 位置: 行 195, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: scripts\setup_i18n.py
- 位置: 行 372, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\chart\interfaces\ichart_manager.py
- 位置: 行 160, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\data\interfaces\idataprocessor.py
- 位置: 行 220, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\i18n\__init__.py
- 位置: 行 342, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\i18n\language_manager.py
- 位置: 行 387, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\i18n\preferences_dialog.py
- 位置: 行 360, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 185, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\factories\visualizer_factory.py
- 位置: 行 232, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\interfaces\ivisualizer.py
- 位置: 行 90, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\config_service.py
- 位置: 行 299, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\config_service_interface.py
- 位置: 行 117, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\data_processing_service_interface.py
- 位置: 行 176, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\document_service_interface.py
- 位置: 行 170, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\event_bus.py
- 位置: 行 272, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\file_service_interface.py
- 位置: 行 152, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\validation_service.py
- 位置: 行 266, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\main\services\validation_service_interface.py
- 位置: 行 122, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py
- 位置: 行 419, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\interfaces\iuiframework.py
- 位置: 行 173, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\modern_battery_viewer.py
- 位置: 行 755, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py
- 位置: 行 637, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 502, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\modern_theme.py
- 位置: 行 272, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\styles\__init__.py
- 位置: 行 22, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\ui\styles\style_manager.py
- 位置: 行 252, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\utils\config_parser.py
- 位置: 行 230, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 文件: src\battery_analysis\utils\environment_utils.py
- 位置: 行 338, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 问题类型: broad-exception-caught
### 问题信息
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 出现次数: 26
- 涉及文件数: 11

### 详细问题列表
#### 文件: scripts\po_translator.py
- 位置: 行 52, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: scripts\run_pylint.py
- 位置: 行 119, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: scripts\run_pylint.py
- 位置: 行 160, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: scripts\run_pylint.py
- 位置: 行 281, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: scripts\run_pylint.py
- 位置: 行 347, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: scripts\run_tests.py
- 位置: 行 64, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\controllers\main_controller.py
- 位置: 行 166, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 100, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 134, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 368, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 87, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 199, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 223, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 268, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 270, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 274, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 293, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 313, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 172, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 370, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 391, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 483, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\ui\modern_theme.py
- 位置: 行 116, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 187, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 219, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 文件: src\battery_analysis\utils\version.py
- 位置: 行 74, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 问题类型: logging-fstring-interpolation
### 问题信息
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 出现次数: 26
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 108, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 114, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 118, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 122, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 150, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 163, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 168, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 171, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 177, 列 36
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 185, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 190, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 197, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 205, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 212, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 219, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 223, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 231, 列 36
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 238, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 245, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 251, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 258, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 173, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 371, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 392, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 481, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 484, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 问题类型: no-name-in-module
### 问题信息
- 类型: error
- 代码: E0611
- 描述: No name 'QFileDialog' in module 'PyQt6.QtWidgets'
- 出现次数: 19
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 25, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFileDialog' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 25, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QMessageBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 27, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'Qt' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QWidget' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QVBoxLayout' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QHBoxLayout' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QPushButton' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QLabel' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QComboBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QCheckBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QGroupBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFrame' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QSizePolicy' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 13, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'Qt' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 13, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'pyqtSignal' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 13, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QSize' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 14, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFont' in module 'PyQt6.QtGui'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 14, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QIcon' in module 'PyQt6.QtGui'
- 符号: no-name-in-module

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 14, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QPixmap' in module 'PyQt6.QtGui'
- 符号: no-name-in-module

## 问题类型: wrong-import-order
### 问题信息
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 出现次数: 19
- 涉及文件数: 3

### 详细问题列表
#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 30, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 31, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 32, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 33, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 34, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 35, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\main\controllers\main_controller.py
- 位置: 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from PyQt6 import QtCore as QC"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 3, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import xlrd as rd" should be placed before "from battery_analysis.utils.exception_type import BatteryAnalysisException"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 4, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 5, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 7, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import re" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import multiprocessing" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import concurrent.futures" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

## 问题类型: unused-import
### 问题信息
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 出现次数: 15
- 涉及文件数: 8

### 详细问题列表
#### 文件: scripts\fix_logging_fstrings.py
- 位置: 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 文件: scripts\po_translator.py
- 位置: 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 文件: scripts\po_translator.py
- 位置: 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 文件: scripts\run_pylint.py
- 位置: 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import re
- 符号: unused-import

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 310, 列 8
- 类型: warning
- 代码: W0611
- 描述: Unused matplotlib.pyplot imported as plt
- 符号: unused-import

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 6, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import re
- 符号: unused-import

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import subprocess
- 符号: unused-import

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QIcon imported from PyQt6.QtGui
- 符号: unused-import

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QPixmap imported from PyQt6.QtGui
- 符号: unused-import

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused matplotlib.pyplot imported as plt
- 符号: unused-import

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 17, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import matplotlib
- 符号: unused-import

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

## 问题类型: wrong-import-position
### 问题信息
- 类型: convention
- 代码: C0413
- 描述: Import "import battery_analysis.utils" should be placed at the top of the module
- 出现次数: 10
- 涉及文件数: 5

### 详细问题列表
#### 文件: src\battery_analysis\__init__.py
- 位置: 行 17, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import battery_analysis.utils" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\main\controllers\main_controller.py
- 位置: 行 6, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import logging" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\main\controllers\main_controller.py
- 位置: 行 7, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from PyQt6 import QtCore as QC" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\main\controllers\main_controller.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.main.workers.analysis_worker import AnalysisWorker" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\ui\styles\__init__.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from .style_manager import StyleManager, style_manager, apply_modern_theme, create_styled_button, create_styled_groupbox" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\utils\plot_utils.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.exception_type import BatteryAnalysisException" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 6, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import logging" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 7, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from docx.oxml import OxmlElement" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from docx.oxml.ns import qn" should be placed at the top of the module
- 符号: wrong-import-position

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 9, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from docx.opc.constants import RELATIONSHIP_TYPE" should be placed at the top of the module
- 符号: wrong-import-position

## 问题类型: missing-module-docstring
### 问题信息
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 出现次数: 9
- 涉及文件数: 9

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\__init__.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\resources\resources_rc.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\utils\csv_utils.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\utils\data_utils.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\utils\excel_utils.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\utils\exception_type.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 文件: src\battery_analysis\utils\plot_utils.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

## 问题类型: import-outside-toplevel
### 问题信息
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.service_container.get_service_container)
- 出现次数: 8
- 涉及文件数: 4

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 27, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.service_container.get_service_container)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 106, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 309, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 310, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.pyplot)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 351, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.pyplot)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 107, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.battery_analysis)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 236, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.file_writer)
- 符号: import-outside-toplevel

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 97, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.resource_manager.ResourceManager)
- 符号: import-outside-toplevel

## 问题类型: too-many-statements
### 问题信息
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (108/50)
- 出现次数: 7
- 涉及文件数: 4

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 94, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (108/50)
- 符号: too-many-statements

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 69, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (140/50)
- 符号: too-many-statements

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 13, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (1012/50)
- 符号: too-many-statements

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1324, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (61/50)
- 符号: too-many-statements

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 25, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (70/50)
- 符号: too-many-statements

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 170, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (76/50)
- 符号: too-many-statements

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 315, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (95/50)
- 符号: too-many-statements

## 问题类型: too-many-nested-blocks
### 问题信息
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 出现次数: 7
- 涉及文件数: 3

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 104, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 104, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 90, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

## 问题类型: f-string-without-interpolation
### 问题信息
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 出现次数: 6
- 涉及文件数: 3

### 详细问题列表
#### 文件: scripts\refactor_by_type.py
- 位置: 行 96, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 文件: scripts\refactor_by_type.py
- 位置: 行 106, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 文件: scripts\run_pylint.py
- 位置: 行 292, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 文件: scripts\run_pylint.py
- 位置: 行 310, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 文件: scripts\run_pylint.py
- 位置: 行 331, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 97, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

## 问题类型: too-many-branches
### 问题信息
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 出现次数: 6
- 涉及文件数: 4

### 详细问题列表
#### 文件: scripts\run_pylint.py
- 位置: 行 285, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 94, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (33/12)
- 符号: too-many-branches

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 69, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (39/12)
- 符号: too-many-branches

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 25, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (14/12)
- 符号: too-many-branches

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 170, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (32/12)
- 符号: too-many-branches

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 315, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (19/12)
- 符号: too-many-branches

## 问题类型: no-else-return
### 问题信息
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 出现次数: 5
- 涉及文件数: 4

### 详细问题列表
#### 文件: scripts\po_translator.py
- 位置: 行 83, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 文件: scripts\po_translator.py
- 位置: 行 151, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 文件: scripts\run_tests.py
- 位置: 行 57, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 43, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 文件: src\battery_analysis\ui\modern_theme.py
- 位置: 行 160, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

## 问题类型: unused-variable
### 问题信息
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'json_output'
- 出现次数: 5
- 涉及文件数: 4

### 详细问题列表
#### 文件: scripts\run_pylint.py
- 位置: 行 175, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'json_output'
- 符号: unused-variable

#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 248, 列 26
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'dirs'
- 符号: unused-variable

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 400, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'chart_styles'
- 符号: unused-variable

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 80, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'paths'
- 符号: unused-variable

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 133, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'paths'
- 符号: unused-variable

## 问题类型: bare-except
### 问题信息
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 出现次数: 4
- 涉及文件数: 2

### 详细问题列表
#### 文件: scripts\po_translator.py
- 位置: 行 134, 列 4
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 165, 列 24
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 188, 列 32
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 196, 列 36
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

## 问题类型: redefined-outer-name
### 问题信息
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'overview' from outer scope (line 121)
- 出现次数: 4
- 涉及文件数: 1

### 详细问题列表
#### 文件: scripts\refactor_by_type.py
- 位置: 行 23, 列 4
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'overview' from outer scope (line 121)
- 符号: redefined-outer-name

#### 文件: scripts\refactor_by_type.py
- 位置: 行 33, 列 4
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'issues_by_type' from outer scope (line 121)
- 符号: redefined-outer-name

#### 文件: scripts\refactor_by_type.py
- 位置: 行 68, 列 28
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'overview' from outer scope (line 121)
- 符号: redefined-outer-name

#### 文件: scripts\refactor_by_type.py
- 位置: 行 68, 列 38
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'issues_by_type' from outer scope (line 121)
- 符号: redefined-outer-name

## 问题类型: too-many-instance-attributes
### 问题信息
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (11/7)
- 出现次数: 4
- 涉及文件数: 4

### 详细问题列表
#### 文件: src\battery_analysis\main\workers\analysis_worker.py
- 位置: 行 14, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (11/7)
- 符号: too-many-instance-attributes

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 26, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (17/7)
- 符号: too-many-instance-attributes

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 12, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (122/7)
- 符号: too-many-instance-attributes

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 24, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (18/7)
- 符号: too-many-instance-attributes

## 问题类型: unidiomatic-typecheck
### 问题信息
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 出现次数: 4
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\utils\csv_utils.py
- 位置: 行 5, 列 7
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 文件: src\battery_analysis\utils\csv_utils.py
- 位置: 行 8, 列 9
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 文件: src\battery_analysis\utils\excel_utils.py
- 位置: 行 10, 列 7
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 文件: src\battery_analysis\utils\excel_utils.py
- 位置: 行 10, 列 35
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

## 问题类型: too-many-lines
### 问题信息
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (2136/1000)
- 出现次数: 3
- 涉及文件数: 3

### 详细问题列表
#### 文件: src\battery_analysis\main\battery_chart_viewer.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (2136/1000)
- 符号: too-many-lines

#### 文件: src\battery_analysis\main\main_window.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (3024/1000)
- 符号: too-many-lines

#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1384/1000)
- 符号: too-many-lines

## 问题类型: syntax-error
### 问题信息
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 417)'
- 出现次数: 3
- 涉及文件数: 3

### 详细问题列表
#### 文件: src\battery_analysis\utils\test_environment_detection.py
- 位置: 行 417, 列 119
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 417)'
- 符号: syntax-error

#### 文件: src\battery_analysis\utils\test_environment_final.py
- 位置: 行 504, 列 149
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 504)'
- 符号: syntax-error

#### 文件: src\battery_analysis\utils\test_environment_scenarios.py
- 位置: 行 473, 列 128
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 473)'
- 符号: syntax-error

## 问题类型: locally-disabled
### 问题信息
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 出现次数: 3
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\utils\version.py
- 位置: 行 133, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 16, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 107, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

## 问题类型: too-many-return-statements
### 问题信息
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (7/6)
- 出现次数: 2
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 57, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (7/6)
- 符号: too-many-return-statements

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 170, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

## 问题类型: protected-access
### 问题信息
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _style_axes of a client class
- 出现次数: 2
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 297, 列 12
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _style_axes of a client class
- 符号: protected-access

#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 309, 列 8
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _style_axes of a client class
- 符号: protected-access

## 问题类型: undefined-variable
### 问题信息
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 出现次数: 2
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\ui\modern_theme.py
- 位置: 行 117, 列 12
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 文件: src\battery_analysis\utils\config_utils.py
- 位置: 行 121, 列 47
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'sys'
- 符号: undefined-variable

## 问题类型: raise-missing-from
### 问题信息
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'处理失败: {str(e)}') from e'
- 出现次数: 2
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 123, 列 32
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 文件: src\battery_analysis\utils\battery_analysis.py
- 位置: 行 139, 列 28
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'并行处理失败: {str(e)}') from e'
- 符号: raise-missing-from

## 问题类型: consider-using-enumerate
### 问题信息
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 出现次数: 2
- 涉及文件数: 2

### 详细问题列表
#### 文件: src\battery_analysis\utils\csv_utils.py
- 位置: 行 10, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 文件: src\battery_analysis\utils\data_utils.py
- 位置: 行 10, 列 4
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

## 问题类型: suppressed-message
### 问题信息
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 16)
- 出现次数: 2
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 16, 列 0
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 16)
- 符号: suppressed-message

#### 文件: src\battery_analysis\utils\word_utils.py
- 位置: 行 107, 列 0
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 107)
- 符号: suppressed-message

## 问题类型: deprecated-method
### 问题信息
- 类型: warning
- 代码: W4902
- 描述: Using deprecated method getdefaultlocale()
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: scripts\po_translator.py
- 位置: 行 130, 列 17
- 类型: warning
- 代码: W4902
- 描述: Using deprecated method getdefaultlocale()
- 符号: deprecated-method

## 问题类型: consider-using-with
### 问题信息
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: scripts\run_pylint.py
- 位置: 行 91, 列 18
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

## 问题类型: subprocess-run-check
### 问题信息
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: scripts\run_tests.py
- 位置: 行 42, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

## 问题类型: unspecified-encoding
### 问题信息
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\validation_controller.py
- 位置: 行 131, 列 17
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

## 问题类型: broad-exception-raised
### 问题信息
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\main\controllers\visualizer_controller.py
- 位置: 行 277, 列 12
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

## 问题类型: redefined-builtin
### 问题信息
- 类型: warning
- 代码: W0622
- 描述: Redefining built-in 'format'
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\ui\modern_chart_widget.py
- 位置: 行 474, 列 37
- 类型: warning
- 代码: W0622
- 描述: Redefining built-in 'format'
- 符号: redefined-builtin

## 问题类型: useless-object-inheritance
### 问题信息
- 类型: refactor
- 代码: R0205
- 描述: Class 'Ui_MainWindow' inherits from object, can be safely removed from bases in python3
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\ui\ui_main_window.py
- 位置: 行 12, 列 0
- 类型: refactor
- 代码: R0205
- 描述: Class 'Ui_MainWindow' inherits from object, can be safely removed from bases in python3
- 符号: useless-object-inheritance

## 问题类型: pointless-string-statement
### 问题信息
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 出现次数: 1
- 涉及文件数: 1

### 详细问题列表
#### 文件: src\battery_analysis\utils\plot_utils.py
- 位置: 行 11, 列 0
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

