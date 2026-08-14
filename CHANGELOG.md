### v2.14.0

#### 功能增强
- feat: 电池按钮正序排列，名称分隔符 `_` 改为 `-`

#### 修复和改进
- fix: 主窗口构造时即初始化 logger，避免 `_deferred_init` 前访问崩溃
- fix: 修复电池按钮排序方向与点击串扰
- fix: 修复 FancyBboxPatch pad 过大导致按钮视觉扩张
- fix: 移除 plt_figure 激进窗口操作，修复多显示器 DPI 下控件点击偏移

#### 重构优化
- refactor: 统一版本单一来源，版本号由 `_version.py` 提供

#### 测试
- test: 适配重构后的 API 并修复 Qt pending timer 残留导致套件卡住

### v2.13.0

#### 功能增强
- feat: 新增电池分类器工具，根据电池规格自动推断电池类型
- feat: 配置对话框改为主从结构，规则表支持按行编辑，规格改为派生只读
- feat: 默认语言锁定为英文，重建 en / zh_CN 翻译目录

#### i18n 国际化
- i18n: 将运行时硬编码中文消息全部改为英文 msgid
- i18n: 收紧 msgid 提取正则，新增翻译目录回环测试

#### 重构优化
- refactor: 移除冗余 LanguageHandler，语言切换由主窗口统一处理
- refactor: 移除未集成的 i18n/application/visualizer 服务与 clean-architecture 骨架
- refactor: 配置加载统一经 ConfigService 路由，清除自定义配置路径缓存

#### Bug Fixes
- fix: 构造方法下拉框仅 Pouch Cell 启用并回填，Coin Cell 禁用并清空
- fix: 校验失败字段高亮覆盖所有必填字段（含下拉框、数值框）
- fix: 输入校验失败时逐条列出真实失败字段，不再误报 Reported By
- fix: 首次运行时从规则派生默认电池规格，避免空界面
- fix: 测试前先收集设备，确保派生位置使用最新数据
- fix: 修复状态栏重翻译哨兵，菜单切换语言后重译失效

### v2.12.2 (Released)

#### Bug Fixes
- fix: 静默 openpyxl "Workbook contains no default style" 警告，消除日志噪音
- fix: 解决循环导入——将共享常量拆分为独立 constants.py 模块

#### 重构优化
- refactor: 清理重复代码——strFileCurrentType循环、matplotlib字体、颜色数组
- refactor: 清理冗余代码，总计 -1,911 行

#### 清理
- chore: 删除不再使用的测试文件以清理代码库

### v2.12.1 (Released)

#### Bug Fixes
- fix: Minor bug fixes and stability improvements

### v2.12.0

#### 功能增强
- feat: 实现无边框UI设计，采用暖色调米色配色方案
- feat: 重构初始化管理器和协调器，支持按阶段分组的模块化初始化流程
- feat: 重构路径提供和统计计算模块，优化代码结构和依赖关系
- feat: 添加数据过滤、Excel处理、日期解析和绘图等实用工具函数
- feat: 精简主窗口组件获取方法，移除冗余文档和异常处理
- feat: 添加创建示例XLSX文件功能，供测试使用
- feat: 删除不必要的图标及资源文件，优化样式管理和路径解析

#### 重构优化
- refactor: 优化XlsxWordWriter方法，提高清晰度和功能
- refactor: 重构电池分析测试并添加实用工具函数

#### 修复和改进
- fix: 修正测试用例中的路径引用，确保正确加载图标和语言管理
- fix: 更新CI-CD配置以支持offscreen渲染，优化端到端测试中的QApplication实例管理

#### 构建和CI/CD
- ci: 修复CI-CD流水线，修复测试失败并排除手动测试，升级至Node.js 24
- ci: 修复wiki初始化路径中的git用户配置和secrets引用

### v2.11.0

#### 功能增强
- feat: 根据电池规格自动判定温度类型（280→Freezer/-20°C，380→Room Temperature）
- feat(配置): 新增电池型号 CR2450HE1、CR2450HE4
- feat(配置): 新增测试设备信息 Liba M1（QA）
- feat(配置): 更新制造商 GP&LB 替代 LBA
- feat(配置): 更新 VGFernitz 设备序列号和硬件/固件版本

#### 配置迁移
- fix: 将 setting.ini 配置系统替换为 JSON，移除对旧 INI 文件的运行时依赖
- fix: 更新 preferences_dialog 配置标签页支持 JSON 配置文件
- fix: 更新 config_utils.find_config_file 默认文件名从 setting.ini 改为 config.json
- fix: 在 Event.__init__ 中用 time.time() 替换废弃的 asyncio.get_event_loop()

#### 清理
- chore: 移除已废弃的 setting.ini、构建残留和迁移计划文档
- chore: 移除死代码 get_item()（零调用者）
- chore: 移除 build.py 中已死亡的 CaseSensitiveConfigParser 类
- refactor: 移除 `_initialize_current_and_voltage_levels` 和 `load_user_settings` 死代码

#### 文档
- docs: 更新 README 配置说明为 JSON 配置系统
- docs: 更新 NUITKA_BUILD.md 版本号至 2.10.0

### v2.9.0

#### 功能增强
- feat: 新增图表写入模块(plot writer)，支持电池数据可视化输出
- feat(日志管理器): 添加日志文件删除重试机制以处理文件锁问题

#### 修复和改进
- fix(Excel写入): 优化常规数据列和超链接处理逻辑
- fix(图表标题): 重构标题生成逻辑，使用统一的build_plot_title函数构建图表标题
- fix(图表标题): 添加动态标题支持，通过元数据文件更新图表标题
- fix(图表标题): 简化标题获取过程并添加默认值处理
- fix(环境信息): 确保清空并更新主窗口的环境信息
- fix(服务依赖图): 优化拓扑排序逻辑，增强对循环依赖的检测
- fix(matplotlib): 更新字体配置以支持emoji显示
- fix: 将日志级别从INFO更改为WARNING，减少日志输出
- fix: 改进异常处理和错误提示
- fix: 增强Excel文件解析的健壮性和错误处理

### v2.8.2

#### 功能增强
- feat: 添加Nuitka打包指南和打包脚本，优化打包流程
- feat(配置): 添加配置管理功能并优化UI组件初始化
- feat(battery_chart_viewer): 添加动态调整纵轴范围功能
- feat(缓存): 为FileService和DataProcessor添加缓存机制

#### 修复和改进
- fix(battery_chart_viewer): 优化动态调整Y轴范围和刻度间隔逻辑
- fix(ci): 修复 GitHub Actions 中 secrets.GH_PAT 的条件判断语法

#### 性能优化
- perf(data_processor): 优化DataFrame内存使用以减少内存消耗

#### 重构优化
- refactor: 清理临时测试脚本和过时文档，精简项目结构

#### 构建和CI/CD
- build: 升级版本至2.8.0
- ci(workflow): 改进wiki同步工作流的可靠性和健壮性

#### 文档
- docs: 添加NUITKA_BUILD.md打包指南
- docs: 添加CHANGELOG维护指南
- docs: 精简和整合文档目录，删除历史报告文档

### v2.8.1

#### 修复和改进
- fix(文件写入): 确保输出目录存在，自动创建缺失的目录
- fix(分析工作线程): 确保输出根目录存在，添加目录创建逻辑
- fix(配置): 修复自定义配置路径切换时的缓存同步问题
- fix(配置): 更新电池配置文件，修正规格类型和测试信息

#### 重构优化
- refactor: 日志等级从 info 调整为 debug，优化性能和日志输出

#### 构建和CI/CD
- build: 升级版本至2.8.1

### v2.8.0

#### 功能增强
- feat: 添加自定义配置文件路径功能
- feat(ui): 新增 Specification Type/Method/Manufacturer 等下拉框组件
- feat(i18n): 增强偏好设置对话框的国际化支持
- feat(validation): 增强验证管理器功能

#### 构建和CI/CD
- build: 升级版本至2.8.0

### v2.7.0

#### 功能增强
- feat: 增强配置值解析逻辑并修复路径配置
- feat(多语言支持): 添加语言处理器并更新配置
- feat(配置管理): 为配置文件查找添加缓存选项

#### 重构优化
- refactor(环境适配): 将环境相关方法提取到独立的环境适配器模块
- refactor(信号处理): 将线程状态处理逻辑从主窗口移至信号连接器
- refactor(ui): 将缩放功能移至menu_manager并清理主窗口代码
- refactor(ui_manager): 将用户设置加载功能从主窗口移至UI管理器
- refactor(信号连接): 将信号连接逻辑提取到独立的SignalConnector类
- refactor(progress_dialog): 将进度对话框类移至独立模块并更新配置
- refactor(ui): 将状态栏消息更新和菜单连接逻辑移至menu_manager
- refactor(main_window): 将工具栏和菜单功能委托给menu_manager

#### 修复和改进
- fix: 简化窗口标题生成逻辑，移除国际化支持
- fix: 解决循环导入问题并优化控制器初始化

#### 构建和CI/CD
- build: 升级版本至2.7.0

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