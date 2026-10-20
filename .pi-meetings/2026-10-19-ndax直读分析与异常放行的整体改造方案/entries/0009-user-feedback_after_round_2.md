# User (Feedback after Round 2): 质疑旧结果覆盖：现有版本号递增机制

# 用户原话

> 原来不是有，往后面增加版本号的代码逻辑吗？你查查

# 主持人现代码核查（供 Round 3 必读）

- `src/battery_analysis/main/business_logic/version_manager.py:105-129`：SHA256.csv 以输入校验和记录主/次版本；相同校验和从 times 取次版本，新校验和追加主版本；`set_version():221-327` 在分析完成信号后将当前 checksum 的次版本 +1 并更新 UI 与 SHA256.csv。
- `src/battery_analysis/main/utils/signal_connector.py:76`：`main_controller.analysis_completed.connect(version_manager.set_version)`；`main/controllers/main_controller.py:83-89,137-144`：worker 的 `thread_end` 信号触发 `analysis_completed`；`main/workers/analysis_worker.py:261-280`：finally 中不论成功、错误、取消均发送 `thread_end`。所以现有版本号确实会往后递增（如 1.0→1.1），但也可能失败/取消时递增，并不是「生成成功」才递增。
- `analysis_worker.py:112-118,173-186` 仍有两处对 `v{version}` 临时目录/`{date}_v{version}` 正式目录的 `rmtree`；当版本重复时会覆盖，但**正常连续重跑**已有递增机制通常可避免碰撞。此前「同样数据再跑必覆盖旧报告」的说法不准确。
- 当前版本计算仍从 `2_xlsx` 扫文件（`version_manager.py:68-84`），未来改 ndax 后要维持现有版本语义、确保异步 checksum 与用户按 Run 时序一致；不要贸然另加 `_r{n}` 后缀以破坏报告命名和路径拼接。Round 3 需要重新评估同名保护最低改动：保留版本号递增为主机制，在写前检查碰撞、安全处理；全部报告路径一次决议并统一传入写入器；不删除旧报告。不要把自己的新后缀方案说成现有代码。