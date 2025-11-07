#### V 1.0.0.0

​	First release.

#### V 1.0.0.1

​	lineEdit_BatchDateCode can input letters.

#### V 1.0.0.2

​	Update graph line name in <u>*BatteryTest-ImageMaker.exe*</u>.

#### V 1.0.0.3

1. Add new battery type: *<u>CP224642(-920@2mA)</u>*
2. Pouch cell's <u>*Datasheet Nominal Capacity*</u> and <u>*Calculation Nominal Capacity*</u> set to **920mAh**, and its *<u>Required Useable Capacity</u>* is **80%** * <u>*Calculation Nominal Capacity*</u>.
3. Pouch cell add cut-off voltage **2.4V**.
4. Update <u>*Sample.xlsx*</u>, <u>*Result.xlsx*</u> and <u>*Result.csv*</u>.
5. Create *<u>.png</u>* instead of *<u>.svg</u>*.
6. Automatically set the *<u>Specification Type</u>* according to the <u>*Battery Type*</u>.

#### V 1.0.0.4

​	Update *\__build__.py*.

#### V 1.0.0.5

1. Update the default saved <u>*.png*</u> name in the PLT program.
2. Coin cell add cut-off voltage **2.4V**.
3. Update <u>*Sample.xlsx*</u>.

#### V 1.0.0.6

​	Update <u>*(un)FilteredLoadVoltageOverCharge.png*</u> and <u>*plt_ (un)FilteredLoadVoltageOverCharge*</u>.

#### V 1.0.0.7

​	<u>*plt_ (un)FilteredLoadVoltageOverCharge*</u>'s title name: pouch cell is @<u>*2.0mA*</u>.

#### V 1.0.0.8

​	Add <u>*.svg*</u> image.

#### V 1.0.0.9

​	Add <u>*.json*</u> file.

#### V 1.0.0.10

1. Add <u>*.docx*</u> report file.
2. Refactor the <u>*src/battery_analysis/utils/battery_analysis.py*</u>, <u>*src/battery_analysis/utils/exception_type.py*</u>, <u>*src/battery_analysis/utils/file_writer.py*</u>, <u>*src/battery_analysis/utils/version.py*</u> code.
3. Update GUI.

#### V 1.0.0.11

​	fix *\__build__.py* bug.

#### V 1.0.0.12

​	fix the bug that <u>*src/battery_analysis/main/main_window.py*</u> raise an unexpected exception.

#### V 1.0.0.13

​	fix the bug which convert <u>*CP224642A*</u> to <u>*CP224642*</u>, but we need <u>*CP224642A*</u>.

#### V 1.0.0.14

​	fix the bug that <u>*.docx*</u> report file has a wrong actual measured minimum capacity percentage.

#### V 1.0.0.15

1. <u>*.ini*</u> file add test information of different tester location, automatically set <u>*tableWidget_TestInformation*</u> when choose <u>*comboBox_TesterLocation*</u>.
2. fix some bugs and update format of <u>*.docx*</u> report file.

#### V 1.0.0.16

​	fix the bug that write <u>*\u2103(℃)*</u> to <u>*.docx*</u> report file lead to an unexpected <u>*space_after*</u>, so add <u>*℃*</u> to sample <u>*.docx*</u> report file and don't write it anymore.

#### V 1.0.0.17

1. Automatically save <u>*tableWidget_TestInformation*</u> without <u>*Enter*</u> when click <u>*Run*</u>.
2. If <u>*strTestInformation*</u> is "", don't save the section to avoid generate <u>*[General]*</u> senction in <u>*setting.ini*</u>.

#### V 1.0.0.18

1. Set a threshold when check pulse current because the <u>*.xlsx*</u> data files may have non-standard pulse current.
2. Update *\__build__.py* a function that build a test version application.

#### V 1.0.0.19

1. Format code.
2. Update *\__build__.py*, add version infomation to *<u>BatteryTest-DataConverter.exe</u>*, so that it won't get version from *<u>setting.in</u>i* any more.
3. *<u>lineEdit_Temperature</u>* can input letter now.
4. In <u>*Sample.xlsx*</u>, if test is pass, <u>*Remarks*</u> shows "OK" instead of "Take as reference".
5. <u>*Report.docx*</u> add version number.

#### V 1.0.0.20

1. Fix version bug in  *\__build__.py*.

#### V 1.0.0.21

1. Automatically fill <u>*lineEdits*</u> after selecting input and output path, analysis version is set by input <u>*.xlsx*</u> checksum and executed times.
2. Update <u>*src/battery_analysis/main/main_window.py*</u> checker.
3. Update <u>*src/battery_analysis/main/main_window.py*</u> and <u>*src/battery_analysis/ui/ui_main_window.py*</u>.
4. Update directory structure and rename <u>*Report.docx*</u>'s name.

#### V 1.0.0.22

1. Update <u>*Main_ImageShow.py*</u> and <u>*PltConfig/Title*</u> to adapt different pulse current.
2. Set default test profile as "Not provided".

#### V 1.0.0.23

1. Update <u>*MD5.csv*</u> as a hidden file.
2. Select the maximum pulse current's <u>*μ -2σ*</u> as the reference value to calculate.

#### V 1.0.0.24

1. Add interface for <u>*RequiredUseableCapacity*</u>.

#### V 1.0.0.25

1. rename <u>*sample.docx*</u>, delete "_V1.0".
2. update for large capacity batteries.

#### V 1.0.0.26

1. add more colors for drawing graph when the number of current level > 4.
2. add a new sample word file and use it when the number of current level > 4.

#### V 1.0.0.27
1. update the accuracy judgment method.

#### V 1.0.0.28
1. fix calculate mean +/- (2/3 * )std value issue.

#### V 1.0.0.29
1. add virtual environment support
2. fix a typo

#### V 1.0.1.0
