# 主持 (Final): Final 全部裁决收口（裁决①-⑦ + 拍板记录）

# Final：全部裁决收口（主持人汇总）

## 裁决① 档位数相同的档值不一致（设定值层，0 容差）
- 阻断 + [以ndax档位为准继续] 按钮，默认焦点 [中止]
- 放行写 Info_Plot.json.profile_validation 留痕（mismatch_type 档值类）
- 依据：Round 2 四家共识；ndax 是完整配方，同一逻辑可放行

## 裁决② 实测层偏差
- 实测脉冲中位数偏差 > max(1%, 0.5mA) → 黄色告警放行 + 留痕（Round 2 四家共识，不变）

## 裁决③ 多 ndax 文件间档位不一致
- **硬报错，不能运行**，提示用户检查数据
- 不给任何放行选项（替代 Round 2 的剔除文件/基准文件方案，用户拍板）

## 裁决④ 档位数不一致（profile 档数 ≠ ndax 档数）—— Round 3 + 用户三项拍板
Round 3 四家 4/4 一致「有条件给」：分界线是数据完整性，不是档位数本身；用 Step.xml 工步完成状态做客观仲裁（机器判，非用户猜）。

```
ndax档数 > profile档数
  → 直接给 [以ndax准继续] 按钮                    【用户拍板：采三家方案，不查工步】
     （数据完整、profile 陈旧；操作员临时加档不被误杀）

ndax档数 < profile档数
  → 查 Step.xml 工步完成状态
     ├─ 全部完成 → 给按钮（协议精简，非截断）
     │            留痕 mismatch_type = level_count_mismatch_complete
     └─ 存在未完成工步 → 硬阻断，报错"测试可能未跑完，请检查数据"
                          mismatch_type = level_count_mismatch_truncated

Step.xml 缺失 / 字段不可读 / 解析失败
  → 硬阻断（无证据=不可放行）                     【用户拍板：从严】
```

- 放行一律复用裁决①交互：默认焦点 [中止]、写 Info_Plot.json.profile_validation、policy_version 沿用 "2026.10"
- **不引入 data.ndc 实测佐证**（用户拍板：Step.xml 工步状态已足够，避免解析私有二进制的复杂度与性能成本）
- mismatch_type 取值补全：`level_count_mismatch_complete` / `level_count_mismatch_truncated` / `level_count_missing_evidence`（Step.xml 缺失）
- 实现量约 15-20 行，一个判定函数（如 check_step_completeness(step_xml)），无新依赖、不新建弹窗（完整分支复用裁决①三按钮弹窗，截断分支复用报错对话框）

## 裁决⑤ 字段/键名统一（用户已同意，Round 2）
- Info_Plot.json：`profile_validation`（result / mismatch_type / decision / policy_version）
- QSettings：`validation/profile_disclaimer_version`，版本值 `"2026.10"`

## 裁决⑥ 中间格式（Round 2 四家全票改判）
- 内存 DataFrame 直传（nda.read → 分析管线），xlsx 退出主链路
- 按需导出 xlsx 落 3_analysis results/{date}_v{ver}/（复用降级按钮/复选框，审计用途）
- 不用 OS 临时目录（会被清理且不更快）；临时目录只放可再生调试 dump

## 裁决⑦ P0 前置修复（Round 2 四家全票）
- filter_data 空档位防御必修：循环头空判 `append([]) continue`，上游空档位与下游过滤逻辑解耦
- 裁决④场景 C（截断）与 P0 各管一层：P0 防崩溃是底线，裁决④决定该不该出报告

## 已裁决不重开项
- 无 profile 时：弹框声明一次（QSettings 记忆版本号），允许继续只靠 ndax 分析
- 重新识别边界：档位/CC电流/型号/批次/日期以 ndax 为准；制造商/成组方式等非分析字段 UI 人为配置，filename_parser 其余调用点不动
- filter_data 修法、多 ndax 硬阻断、字段命名：均定案

---
会议状态：全部议题收敛，无残余分歧。四轮（Round 1 提案评估 → Round 2 四议题收敛 → 用户裁决 → Round 3 单点补辩 + 用户三项拍板）完成。
