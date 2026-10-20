# User (Feedback after Round 3): 日期与档位的唯一来源、目录与版本命名

# 用户原话

> 同意你的三条建议，只是档位直接从 Step.xml 取，测试日期听你的第一条建议

# 明确裁决

1. 脉冲档位直接从每个 ndax 内的 `Step.xml` 读取；不从文件名或 xlsx 推定。
2. 报告测试日期从 ndax 实测数据的 Timestamp 按一个统一规则确定；选定的日期规范化、校验为 YYYYMMDD 后，仅决定一次。worker 将同一个 test_date/result_dir 显式传给 ReportCoordinator、JsonWriter 等所有写入器，禁止各自从电池名、时间戳另起一套目录。
3. 版本继续采用 SHA256.csv 既有主/次递增，只有全部报告成功才加次版本；内部路径小写 v，正式目录 `{YYYYMMDD}_v{版本}`。不必擅改现有报告交付文件名称里的大写 V。
4. Step.xml 不作为实际测试日期的权威来源。本反馈细化此前 Round 3 日期来源未决项。尚未明确授权编写 conclusion.md 或修改源码，按会议协议等确认。
