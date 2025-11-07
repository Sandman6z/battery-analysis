import os
import csv
import datetime
import traceback

import xlrd as rd

from src.battery_analysis.utils.exception_type import BatteryAnalysisException


class BatteryAnalysis:
    def __init__(self, strInDataXlsxDir: str, strResultPath: str, listTestInfo: list) -> None:
        # list for current level and voltage level, next get them in main_window.py
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.strFileCurrentType = ""
        for c in range(len(self.listCurrentLevel)):
            self.strFileCurrentType = self.strFileCurrentType + f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]

        # input .xlsx directory and result txt path
        self.strInDataXlsxDir = f"{strInDataXlsxDir}/"
        self.strResultLogTxt = f"{strResultPath}/V{listTestInfo[16]}/{listTestInfo[4]}_{listTestInfo[2]}_{listTestInfo[3]}_{self.strFileCurrentType}_{listTestInfo[7]}.txt"

        # list to store all battery charge
        self.listAllBatteryCharge = []
        # list for all battery name
        self.listBatteryName = []
        # list for time stamp
        self.listTimeStamp = []

        # list for Info_Iamge.csv, use the .csv to draw line chart
        self.listAllPosiForInfoImageCsv = []
        self.listAllChargeForInfoImageCsv = []
        self.listAllVoltageForInfoImageCsv = []

        # str for error log
        self.strErrorLog = ""

        try:
            # get all input .xlsx path
            self.listAllInXlsx = [self.strInDataXlsxDir + f for f in os.listdir(self.strInDataXlsxDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            # print(self.listAllInXlsx)

            if len(self.listAllInXlsx) == 0:
                raise BatteryAnalysisException("[Input Path Error]: has no data file")

            # analysis every battery data 
            for i in range(len(self.listAllInXlsx)):
                self.UBA_AnalysisXlsx(self.listAllInXlsx[i])

            # write .csv for draw line chart
            self.UBA_WriteCsv(f"{strResultPath}/V{listTestInfo[16]}")

        except BaseException as e:
            self.strErrorLog = str(e)
            traceback.print_exc()

    def UBA_AnalysisXlsx(self, strPath: str) -> None:
        # temp list to store voltage and row refer to different current level and voltage level
        listLevelToVoltage = []
        listLevelToRow = []
        listLevelToCharge = []
        # temp list to store every battery info for .csv
        listPosiForInfoImageCsv = []
        listVoltageForInfoImageCsv = []
        listChargeForInfoImageCsv = []

        # init list
        for c in range(len(self.listCurrentLevel)):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            listLevelToCharge.append([])
            listPosiForInfoImageCsv.append([])
            listVoltageForInfoImageCsv.append([])
            listChargeForInfoImageCsv.append([])
            for v in range(len(self.listVoltageLevel)):
                listLevelToVoltage[c].append(self.listVoltageLevel[v])
                listLevelToRow[c].append(0)
                listLevelToCharge[c].append(0)

        # read workbook
        rb = rd.open_workbook(strPath)
        # cycle sheet
        cycleTable = rb.sheets()[0]
        cycleRows = cycleTable.nrows
        cycleCycle = cycleTable.col_values(0)
        cycleBegin = cycleTable.col_values(1)
        cycleEnd = cycleTable.col_values(2)
        cycleCharge = cycleTable.col_values(3)
        # step sheet
        stepTable = rb.sheets()[1]
        stepRows = stepTable.nrows
        stepCycle = stepTable.col_values(0)
        stepStep = stepTable.col_values(1)
        stepCharge = stepTable.col_values(2)
        # record sheet
        recordTable = rb.sheets()[2]
        recordRows = recordTable.nrows
        recordCycle = recordTable.col_values(0)
        recordStep = recordTable.col_values(1)
        recordCurrent = recordTable.col_values(2)
        recordVoltage = recordTable.col_values(3)
        recordCharge = recordTable.col_values(4)

        def strCompareDate(_strDate1: str, _strDate2: str, _bEarlier: bool) -> str:
            def intConvertDate(_strDate: str) -> int:
                _cd1 = _strDate.split(" ")[0].split("-")
                _cd2 = _strDate.split(" ")[1].split(":")
                return int("{}{:02}{:02}{:02}{:02}{:02}".format(int(_cd1[0]), int(_cd1[1]), int(_cd1[2]),
                                                                int(_cd2[0]), int(_cd2[1]), int(_cd2[2])))

            if _strDate1 == _strDate2:
                _min_date = _strDate1
                _max_date = _strDate2
            else:
                _convert_date1 = intConvertDate(_strDate1)
                _convert_date2 = intConvertDate(_strDate2)
                if _convert_date1 < _convert_date2:
                    _min_date = _strDate1
                    _max_date = _strDate2
                else:
                    _min_date = _strDate2
                    _max_date = _strDate1
            if _bEarlier:
                return _min_date
            else:
                return _max_date

        # first battery, not need compare
        if not self.listTimeStamp:
            self.listTimeStamp.append(cycleBegin[2])
            self.listTimeStamp.append(cycleEnd[-1])
        else:
            # compare start time stamp
            self.listTimeStamp[0] = strCompareDate(cycleBegin[2], self.listTimeStamp[0], True)
            # compare end time stamp
            self.listTimeStamp[1] = strCompareDate(cycleEnd[-1], self.listTimeStamp[1], False)
        # print(self.listTimeStamp)

        def bIsInRangeMilliAmpere(_floatInput: float, _floatStandard: float):
            _floatMin = _floatStandard*1.05
            _floatMax = _floatStandard*0.95
            if _floatMin <= _floatInput <= _floatMax:
                return True
            else:
                return False

        # analysis battery data
        self.listBatteryName.append(cycleCycle[0])
        for row in range(2, recordRows):
            if recordStep[row] != "脉冲" and recordStep[row] != "Pulse":
                pass
            else:
                for c in range(len(self.listCurrentLevel)):
                    if bIsInRangeMilliAmpere(float(recordCurrent[row]) * 1000, -float(self.listCurrentLevel[c])):
                        if row < recordRows - 1:
                            if not bIsInRangeMilliAmpere(float(recordCurrent[row + 1]) * 1000, -float(self.listCurrentLevel[c])):
                                listPosiForInfoImageCsv[c].append(row)
                                listVoltageForInfoImageCsv[c].append(recordVoltage[row])
                        for v in range(len(self.listVoltageLevel)):
                            if float(recordVoltage[row]) <= self.listVoltageLevel[v]:
                                if listLevelToRow[c][v] == 0:
                                    listLevelToVoltage[c][v] = float(recordVoltage[row])
                                    listLevelToRow[c][v] = row

        self.UBA_Log(datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S]") + '\r')
        self.UBA_Log("Battery {}:\r".format(self.listBatteryName[-1]))
        for c in range(len(self.listCurrentLevel)):
            self.UBA_Log("{}mA - ".format(self.listCurrentLevel[c]))
            for v in range(len(self.listVoltageLevel)):
                self.UBA_Log("{}:{}, ".format(
                    listLevelToVoltage[c][v], listLevelToRow[c][v] and listLevelToRow[c][v] + 1 or listLevelToRow[c][v]))
            self.UBA_Log("\r")

        # for Utility_XlsxWriter.py to write .xlsx
        listOneBatteryCharge = []

        def Posi2Charge(intPosi: int, intCharge: int):
            if intPosi:
                _cycle = recordCycle[intPosi]
                for _c1 in range(2, cycleRows):
                    if cycleCycle[_c1] < _cycle:
                        intCharge += abs(cycleCharge[_c1])
                    if cycleCycle[_c1] >= _cycle:
                        break
                for _c2 in range(2, stepRows):
                    if stepCycle[_c2] == _cycle:
                        if stepStep[_c2] != "脉冲" and stepStep[_c2] != "Pulse":
                            intCharge += abs(stepCharge[_c2])
                    if stepCycle[_c2] > _cycle:
                        break
                intCharge += abs(recordCharge[intPosi])
                listOneBatteryCharge.append(round(intCharge))
            else:
                listOneBatteryCharge.append(0)

        for c in range(len(self.listCurrentLevel)):
            for v in range(len(self.listVoltageLevel)):
                Posi2Charge(listLevelToRow[c][v], listLevelToCharge[c][v])
        self.listAllBatteryCharge.append(listOneBatteryCharge)
        self.UBA_Log("\r")

        # for Main_ImageShow.py to draw line chart
        def listPosi2Charge(listPosi: list) -> list:
            _listCharge = []
            for _i in range(len(listPosi)):
                _intTempCharge = 0
                _cycle = recordCycle[listPosi[_i]]
                for _c1 in range(2, cycleRows):
                    if cycleCycle[_c1] < _cycle:
                        _intTempCharge += abs(cycleCharge[_c1])
                    if cycleCycle[_c1] >= _cycle:
                        break
                for _c2 in range(2, stepRows):
                    if stepCycle[_c2] == _cycle:
                        if stepStep[_c2] != "脉冲" and stepStep[_c2] != "Pulse":
                            _intTempCharge += abs(stepCharge[_c2])
                    if stepCycle[_c2] > _cycle:
                        break
                _intTempCharge += abs(recordCharge[listPosi[_i]])
                _listCharge.append(_intTempCharge)
            return _listCharge

        for c in range(len(self.listCurrentLevel)):
            listChargeForInfoImageCsv[c] = listPosi2Charge(listPosiForInfoImageCsv[c])
            if len(listChargeForInfoImageCsv[c]) != len(listVoltageForInfoImageCsv[c]):
                raise BatteryAnalysisException("[Plt Data Error]: battery {} {}mA pulse, charge is not equal to voltage"
                                              .format(self.listBatteryName[-1], self.listCurrentLevel[c]))
        self.listAllPosiForInfoImageCsv.append(listPosiForInfoImageCsv)
        self.listAllVoltageForInfoImageCsv.append(listVoltageForInfoImageCsv)
        self.listAllChargeForInfoImageCsv.append(listChargeForInfoImageCsv)

    def UBA_WriteCsv(self, _strResultPath: str) -> None:
        f = open(f"{_strResultPath}/Info_Image.csv", mode='w', newline='', encoding='utf-8')
        csvFile = csv.writer(f)
        for b in range(len(self.listBatteryName)):
            csvFile.writerow(["BATTERY", self.listBatteryName[b]])
            for c in range(len(self.listCurrentLevel)):
                csvFile.writerow(self.listAllPosiForInfoImageCsv[b][c])
                csvFile.writerow(self.listAllChargeForInfoImageCsv[b][c])
                csvFile.writerow(self.listAllVoltageForInfoImageCsv[b][c])
        f.close()

    def UBA_Log(self, _data: str) -> None:
        print(_data, end='')
        f = open(self.strResultLogTxt, "a")
        f.write(_data)
        f.close()

    def UBA_GetBatteryInfo(self) -> list:
        return [self.listAllBatteryCharge, self.listBatteryName, self.listTimeStamp]

    def UBA_GetErrorLog(self) -> str:
        return self.strErrorLog
