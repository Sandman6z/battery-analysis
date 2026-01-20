### v2.6.0

#### 功能增强
- feat: 添加文件验证模块并优化路径管理
- feat(visualization): 增强可视化工具的数据加载和更新检测功能
- feat(配置服务): 为配置文件查找添加缓存选项

#### 重构优化
- refactor: 优化初始化流程并改进模块导入
- refactor(deps): 移除未使用的gitpython依赖
- refactor(config): 在setting.ini中添加配置组命名规范的注释

#### 修复和改进
- fix(battery_analysis): 添加输入参数验证和错误处理
- fix(build): 保留setting.ini原始注释并更新PltConfig配置

#### 构建和CI/CD
- build: 升级版本至2.6.0

### v2.5.0

#### 功能增强
- feat: 实现并行初始化，使用ThreadPoolExecutor优化启动速度
- feat: 移除未使用的依赖，减少打包体积

#### 重构优化
- refactor: 优化代码结构，提高可维护性
- refactor: 改进初始化流程，实现优先级分组和并行执行

#### 构建和CI/CD
- build: 升级版本至2.5.0

### v2.4.1

#### 功能增强
- feat: 优化导入结构，减少启动时的导入时间

#### 重构优化
- refactor: 移除未使用的导入（re, time, matplotlib）
- refactor: 修复UI图标缺失问题，添加resources_rc导入

#### 构建和CI/CD
- build: 禁用UPX压缩以解决构建问题

### v2.4.0

#### 功能增强
- feat: 升级电池分析应用至2.4.0版本并增强日志系统
- feat: 将MD5校验和升级为SHA256以提高安全性

#### 重构优化
- refactor(version_manager): 改进版本管理逻辑，支持SHA256校验和
- refactor: 优化版本计算和更新机制

#### 构建和CI/CD
- ci: 更新CI/CD工作流中的发布信息生成脚本

### v2.3.0

#### 功能增强
- feat(utils): 新增并行处理工具和缓存功能
- feat(应用实例): 实现单例模式防止重复启动应用
- feat(i18n): 增强本地化功能支持显示名称和系统区域检测

#### 重构优化
- refactor(数据分析): 优化数据处理性能并重构组件获取逻辑
- refactor(build): 优化PyInstaller构建配置
- refactor: 优化代码结构和错误处理逻辑
- refactor(utils): 优化变量命名并提取异常检测逻辑
- refactor(数据工具): 重命名变量以符合命名规范

#### 构建和CI/CD
- ci(workflow): 优化CI/CD工作流并改进发布机制
- build: 更新Python版本要求至3.13并优化依赖管理
- fix(build): 更新Python版本至3.13并添加locale目录支持

### v2.2.0
1. 重构版本管理系统，实现中心化版本控制
2. 添加初始化管理器，将主窗口初始化流程重构为模块化步骤
3. 实现命令模式，重构电池分析功能
4. 添加命令管理器和验证管理器
5. 为所有UI控件添加工具提示
6. 将测试配置管理和分析运行逻辑提取到独立管理器类
7. 实现电池测试分析领域核心功能
8. 添加温度处理、路径管理和报告管理功能
9. 按照分层架构重构服务注册和应用服务逻辑
10. 删除过时的架构和UI设计文档，清理代码库
11. 优化代码结构，提高可维护性和模块化程度

### v2.1.4
1. 更新Python版本从3.11到3.13，提升运行性能和兼容性
2. 优化底层依赖管理，确保与Python 3.13兼容
3. 更新项目配置，添加Python 3.12和3.13支持

### v2.1.3
1. 更新版本号至2.1.3
2. 修复报告路径错误问题
3. 优化规格类型匹配逻辑以避免短匹配优先
4. 调整界面布局间距和高度以优化显示效果
5. 将测试者和报告者组合框改为可编辑
6. 优化样式管理并清理冗余代码
7. 添加报告打开功能并优化分析完成提示
8. 修复和新增功能，提升应用稳定性和用户体验

### v2.1.2
1. 更新版本号至2.1.2
2. 优化代码结构和可维护性
3. 完善国际化支持
4. 修复已知bug

### v2.1.1
1. 修复visualizer中图像显示不全的问题（纵坐标从0开始显示）
2. 优化坐标轴配置管理，实现参数可动态调整
3. 修复无XML文件启动时file-open菜单点击无响应的问题
4. 确保无论是否选择XML文件，Open功能始终可用

### v2.1.0
1. 将原来单独的visualizer工具exe功能合并到主UI中，二者合并为同一个exe，减少不必要的空间浪费，也节省了打包时间
2. 优化代码结构，提高可维护性
3. 修复已知bug

### v2.0.0
1. 更新版本号从1.0.1到2.0.0
2. pyqt5 升级到 pyqt6
3. 修复一些 pyqt6 不兼容的问题

### v1.0.1
1. 更新版本号从1.0.0到1.0.1，统一构建版本与GitHub Release版本号

### v1.0.0.29
1. add virtual environment support
2. fix a typo

### v1.0.0.28
1. fix calculate mean +/- (2/3 * )std value issue.

### v1.0.0.27
1. update the accuracy judgment method.

### v1.0.0.26
1. add more colors for drawing graph when the number of current level > 4.
2. add a new sample word file and use it when the number of current level > 4.

### v1.0.0.25
1. rename <u>*sample.docx*</u>, delete "_V1.0".
2. update for large capacity batteries.

### v1.0.0.24
1. Add interface for <u>*RequiredUseableCapacity*</u>.

### v1.0.0.23
1. Update <u>*MD5.csv*</u> as a hidden file.
2. Select the maximum pulse current's <u>*μ -2σ*</u> as the reference value to calculate.

### v1.0.0.22
1. Update <u>*Main_ImageShow.py*</u> and <u>*PltConfig/Title*</u> to adapt different pulse current.
2. Set default test profile as "Not provided".

### v1.0.0.21
1. Automatically fill <u>*lineEdits*</u> after selecting input and output path, analysis version is set by input <u>*.xlsx*</u> checksum and executed times.
2. Update <u>*src/battery_analysis/main/main_window.py*</u> checker.
3. Update <u>*src/battery_analysis/main/main_window.py*</u> and <u>*src/battery_analysis/ui/ui_main_window.py*</u>.
4. Update directory structure and rename <u>*Report.docx*</u>'s name.

### v1.0.0.20
1. Fix version bug in  *\__build__.py*.

### v1.0.0.19
1. Format code.
2. Update *\__build__.py*, add version infomation to *<u>BatteryTest-DataConverter.exe</u>*, so that it won't get version from *<u>setting.in</u>i* any more.
3. *<u>lineEdit_Temperature</u>* can input letter now.
4. In <u>*Sample.xlsx*</u>, if test is pass, <u>*Remarks*</u> shows "OK" instead of "Take as reference".
5. <u>*Report.docx*</u> add version number.

### v1.0.0.18
1. Set a threshold when check pulse current because the <u>*.xlsx*</u> data files may have non-standard pulse current.
2. Update *\__build__.py* a function that build a test version application.

### v1.0.0.17
1. Automatically save <u>*tableWidget_TestInformation*</u> without <u>*Enter*</u> when click <u>*Run*</u>.
2. If <u>*strTestInformation*</u> is "", don't save the section to avoid generate <u>*[General]*</u> senction in <u>*setting.ini*</u>.

### v1.0.0.16
​	fix the bug that write <u>*\u2103(℃)*</u> to <u>*.docx*</u> report file lead to an unexpected <u>*space_after*</u>, so add <u>*℃*</u> to sample <u>*.docx*</u> report file and don't write it anymore.

### v1.0.0.15
1. <u>*.ini*</u> file add test information of different tester location, automatically set <u>*tableWidget_TestInformation*</u> when choose <u>*comboBox_TesterLocation*</u>.
2. fix some bugs and update format of <u>*.docx*</u> report file.

### v1.0.0.14
​	fix the bug that <u>*.docx*</u> report file has a wrong actual measured minimum capacity percentage.

### v1.0.0.13
​	fix the bug which convert <u>*CP224642A*</u> to <u>*CP224642*</u>, but we need <u>*CP224642A*</u>.

### v1.0.0.12
​	fix the bug that <u>*src/battery_analysis/main/main_window.py*</u> raise an unexpected exception.

### v1.0.0.11
​	fix *\__build__.py* bug.

### v1.0.0.10
1. Add <u>*.docx*</u> report file.
2. Refactor the <u>*src/battery_analysis/utils/battery_analysis.py*</u>, <u>*src/battery_analysis/utils/exception_type.py*</u>, <u>*src/battery_analysis/utils/file_writer.py*</u>, <u>*src/battery_analysis/utils/version.py*</u> code.
3. Update GUI.

### v1.0.0.9
​	Add <u>*.json*</u> file.

### v1.0.0.8
​	Add <u>*.svg*</u> image.

### v1.0.0.7
​	<u>*plt_ (un)FilteredLoadVoltageOverCharge*</u>'s title name: pouch cell is @<u>*2.0mA*</u>.

### v1.0.0.6
​	Update <u>*(un)FilteredLoadVoltageOverCharge.png*</u> and <u>*plt_ (un)FilteredLoadVoltageOverCharge*</u>.

### v1.0.0.5
1. Update the default saved <u>*.png*</u> name in the PLT program.
2. Coin cell add cut-off voltage **2.4V**.
3. Update <u>*Sample.xlsx*</u>.

### v1.0.0.4
​	Update *\__build__.py*.

### v1.0.0.3
1. Add new battery type: *<u>CP224642(-920@2mA)</u>*
2. Pouch cell's <u>*Datasheet Nominal Capacity*</u> and <u>*Calculation Nominal Capacity*</u> set to **920mAh**, and its *<u>Required Useable Capacity</u>* is **80%** * <u>*Calculation Nominal Capacity*</u>.
3. Pouch cell add cut-off voltage **2.4V**.
4. Update <u>*Sample.xlsx*</u>, <u>*Result.xlsx*</u> and <u>*Result.csv*</u>.
5. Create *<u>.png</u>* instead of *<u>.svg</u>*.
6. Automatically set the *<u>Specification Type</u>* according to the <u>*Battery Type*</u>.

### v1.0.0.2
​	Update graph line name in <u>*BatteryTest-ImageMaker.exe*</u>.

### v1.0.0.1
​	lineEdit_BatchDateCode can input letters.

### v1.0.0.0
​	First release.