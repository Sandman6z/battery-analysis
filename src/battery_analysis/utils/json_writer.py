import datetime
import json
import logging
import os

from battery_analysis.utils.data_utils import generate_current_type_string


class JsonWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        try:
            [sy, sm, sd] = self.listBatteryInfo[2][0].split(" ")[0].split("-")
            td = f"{sy}{sm}{sd}"
        except ValueError:
            td = "00000000"
        self.strResultPath = f"{strResultPath}/{td}_v{listTestInfo[16]}"
        self.dictJson = {}
        self.listTestRun = []
        self.dictMeasurements = {}
        self.runAt = datetime.datetime.strptime(
            self.listBatteryInfo[2][0], "%Y-%m-%d %H:%M:%S").astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.strFileCurrentType = generate_current_type_string(self.listCurrentLevel)
        # 使用os.path.join确保路径分隔符一致性
        # 替换文件名中的无效字符，特别是冒号
        safe_temperature = self.listTestInfo[7].replace(':', '_')
        self.strResultJsonPath = os.path.join(
            self.strResultPath, f"{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}_{self.strFileCurrentType}_{safe_temperature}.json")
        self.listBatteryVoltage = []
        for v, voltage_level in enumerate(self.listVoltageLevel):
            voltage_str = str(voltage_level)
            formatted_voltage = voltage_str + '0' * (4 - len(voltage_str)) if len(voltage_str) < 4 else voltage_str
            self.listBatteryVoltage.append(formatted_voltage)

        self.UJS_FormatJson()

    def UJS_FormatJson(self) -> None:
        for i, battery_info in enumerate(self.listBatteryInfo[1]):
            index = -1
            dictMeasurements = [{} for _ in self.listCurrentLevel]
            dictTestRun = {}

            # 填充测量数据
            for j, value in enumerate(self.listBatteryInfo[0][i]):
                if j % (len(self.listVoltageLevel)) == 0:
                    index += 1
                if value != 0 and self.listBatteryVoltage[j % len(self.listBatteryVoltage)] != "":
                    voltage_key = self.listBatteryVoltage[j % len(self.listBatteryVoltage)]
                    dictMeasurements[index][voltage_key] = value

            # 生成电池名称
            try:
                battery_name_split = battery_info.split("BTS")[1].split("_")
                battery_name = f"{battery_name_split[2]}_{battery_name_split[3]}"
            except IndexError:
                battery_name = f"Battery_{i}"

            # 构建结果列表
            listResults = [
                {"scenario": f"{current}mA", "measurements": dictMeasurements[c]}
                for c, current in enumerate(self.listCurrentLevel)
            ]

            # 更新测试运行字典并添加到列表
            dictTestRun.update({"slot": battery_name, "results": listResults})
            self.listTestRun.append(dictTestRun)

        strBatteryModel = self.listTestInfo[2]
        # 电池类型基础规格（固定值，用于匹配电池类型分类）
        listBatteryTypeBase = [
            "CoinCell", "ButtonCell", "Cylindrical", "Prismatic", "PouchCell"]
        try:
            strBatteryType = ""
            for battery_type in listBatteryTypeBase:
                if battery_type.strip() in self.listTestInfo[2]:
                    strBatteryType = battery_type
                    break
            if not strBatteryType:
                strBatteryType = "CoinCell"
                logging.warning("未找到精确匹配的电池类型，使用默认值: %s", strBatteryType)
        except (IndexError, TypeError, ValueError) as e:
            logging.error("处理电池类型时发生错误: %s，使用默认值", e)
            strBatteryType = "CoinCell"

        self.dictJson.update({
            "batchId": self.listTestInfo[5],
            "runAt": self.runAt,
            "batteryType": strBatteryType,
            "batteryModel": strBatteryModel,
            "batteryManufacturer": self.listTestInfo[4],
            "testRuns": self.listTestRun})

        # 确保目标目录存在
        os.makedirs(os.path.dirname(self.strResultJsonPath), exist_ok=True)
        with open(self.strResultJsonPath, 'w') as file:
            json.dump(self.dictJson, file, indent=4)
