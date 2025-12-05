import json
import os

# 检查当前目录
print('当前目录:', os.getcwd())

# 检查JSON文件路径
file_path = os.path.join('tests', 'data', 'test_config.json')
print('文件路径:', file_path)
print('文件存在:', os.path.exists(file_path))

# 尝试读取JSON文件
if os.path.exists(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print('JSON解析成功!')
            print('数据类型:', type(data))
            print('包含的键:', list(data.keys()))
            if 'test_scenarios' in data:
                print('测试场景数量:', len(data['test_scenarios']))
            if 'reported_by_mapping' in data:
                print('映射关系:', data['reported_by_mapping'])
    except json.JSONDecodeError as e:
        print('JSON解析错误:', e)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print('文件内容:', repr(content))
