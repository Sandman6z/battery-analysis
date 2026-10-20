# User (Feedback after Round 2): 版本沿用、禁止同名删除、失败取消清半成品

# 用户新裁决（原话）

> 如果目标目录同名就删除”的代码这个逻辑不对，删掉，然后检查删干净。应该是你找到的：version_manager.py 用 SHA256.csv 记录版本；同一份输入完成一次运行后，set_version() 会把次版本往后加，例如 1.0 → 1.1。正常连续运行通常会写到不同版本目录
> 如果失败或者取消的话，应该将生成一半的“半成品”都清理干净，版本保持上一版的

# 主持人要求 Round 3 核查的代码要点

- 删除 `analysis_worker.py` 对 `version_dir` 与 `final_dir` 的两个「存在就 rmtree」行为，不得删旧结果，遇同名目标应安全拒绝而非覆盖；不额外制造 `_r2` 等独立版本体系，沿用 SHA256.csv 主/次版本规则。
- 现 `analysis_worker.py:261-280` finally 无条件发 `thread_end`，controller 在 `_on_analysis_completed` 无条件发 `analysis_completed`，`signal_connector.py:76` 绑定 `version_manager.set_version`，导致失败/取消仍递增版本。必须以“最终全部报告成功产出”为唯一递增条件；取消/失败不更新 UI 版本和 SHA256.csv 已用次数。注意 `get_version()` 扫描时也可能在 SHA256.csv 追加新 checksum，须区分预登记与成功计次。
- 半成品清理范围是本次运行**独占创建**的文件/目录，包括分析中间目录、报告中途产生的正式目录、运行时日志；仅在失败/取消时删自己持有的路径，不能用宽泛 rmtree 清理已有目录。需检查 `BatteryAnalysis` 写 `V{version}`（大写）与 worker 创 `v{version}`（小写）跨平台问题；`ReportCoordinator`/`JsonWriter` 自己重拼 `{td}_v{ver}` 目录，可能写到非 worker 管理路径，先统一路径或校验目的地，避免误清理/留半成品。
- 用户说“删掉，然后检查删干净”在当前黑板讨论会议中作为实施硬约束；会议顾问仍只写方案，未获明确编码阶段授权，不要擅改代码。
