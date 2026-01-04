import json
import collections

with open('pylint_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
issues = [item['symbol'] for item in data]
counter = collections.Counter(issues)

print('问题类型统计：')
for issue, count in counter.most_common(20):
    print(f'{issue}: {count}个问题')
