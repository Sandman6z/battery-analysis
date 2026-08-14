# 双端发布设计：GitHub 构建 + Gitee 源码与 Release 同步

## 背景与目标

项目以 GitHub（`Sandman6z/battery-analysis`）为开发主仓库，Gitee 镜像仓库为 `gitee.com/boedt/battery-analysis`。当前存在三个问题：

1. GitHub 侧 CI/CD 已实现自动构建 exe 并创建 GitHub Release（tag + Release 形态），但 Gitee 仓库长期停留在旧代码。
2. `sync-to-gitee.yaml` 工作流从未真正执行过 Gitee 推送——由于 secrets 未映射到环境变量，检测步骤恒判"未配置"，推送步骤被 `if` 跳过，工作流长期显示 success 但无实际同步。
3. 无 Gitee Release / exe 分发能力。

**目标**：main 分支推送后自动构建 exe 并发布 GitHub Release；同时将源码和 tag 同步到 Gitee，并在 Gitee 创建对应 Release（含 exe 附件）。发布形态保持 GitHub Release 机制（tag + Release），不引入 git 分支。

## 需求澄清结论

| 决策点 | 结论 |
|---|---|
| 发布形态 | 保持 GitHub Release（tag + Release + exe 附件），不建 git 分支 |
| Gitee 同步粒度 | 全量同步：每次 main push（`vX.Y.Z-beta.SHA` 预发布）与正式 tag（`vX.Y.Z`）都同步源码并创建 Gitee Release |
| Gitee prerelease 状态 | 与 GitHub 一致：beta 版本在 Gitee 也标记为预发布 |
| 方案架构 | A：GitHub job 内联 Gitee 发布（推荐） |
| Gitee token | 需重新生成具备 projects 全权能的私人令牌 |

## 架构

两个工作流分工：

- **`ci-cd.yaml`**：构建 + 双端发布。`build-and-test` 构建 exe，`release` job 创建 GitHub Release 并上传 exe 后，追加 Gitee API 步骤创建对应 Gitee Release 并上传同一 exe。
- **`sync-to-gitee.yaml`**：职责收敛为只同步源码和 tag（`git push`），不触碰 Release。修复现有 bug 使同步真正执行。

### 数据流（以 tag `v2.14.0` 为例）

```
push v2.14.0 (GitHub)
  → ci-cd.yaml:
      build-and-test: 构建 exe → build/Release/battery-analyzer_2.14.0_x64.exe
      release: 创建 GitHub Release v2.14.0（上传 exe）
             → 调 Gitee API: 创建 Gitee Release v2.14.0（上传同一 exe）
  → sync-to-gitee.yaml:
      push main + v2.14.0 tag 到 Gitee（源码）
```

main push 流程相同，只是 Release 名带 `-beta.SHA` 后缀且标记为 prerelease。

## `ci-cd.yaml` 扩展

### release job 追加步骤

在现有 "Create GitHub Release and Upload Assets"（`actions/github-script@v7`）之后新增一个步骤：

1. 从 `build/Release/` 定位 `*.exe`（与 GitHub 上传逻辑一致）。
2. 解析版本名：复用现有 `release_info` 步骤的 `release_name` 输出（如 `v2.14.0` 或 `v2.14.0-beta.abc123`）与 `is_prerelease`。
3. 调 Gitee API 创建 Release：

   ```
   POST https://gitee.com/api/v5/repos/boedt/battery-analysis/releases
   body: { access_token, tag_name, name, body, prerelease, target_commitish }
   ```

   - `tag_name` 与 GitHub 的 release 名一致。
   - 若 Gitee 已存在同名 Release，先删除（`DELETE /repos/{owner}/{repo}/releases/{id}`，需先按 tag 查询 `GET /repos/{owner}/{repo}/releases/tags/{tag}`）再创建，保证幂等。
4. 上传 exe 附件（multipart）：

   ```
   POST https://gitee.com/api/v5/repos/boedt/battery-analysis/releases/{release_id}/attach_files
   form: { access_token, file }
   ```

5. 记录日志；失败不阻断 GitHub Release。

### 凭据

- 需要 `GITEE_USERNAME`、`GITEE_TOKEN` secrets 映射到 job `env`（与 `sync-to-gitee` 修复相同手法）。
- 上传脚本建议用 PowerShell + `Invoke-RestMethod`（runner 为 windows-latest），或 `actions/github-script` 内 `fetch`。

## `sync-to-gitee.yaml` 修复

修复以下问题使其真正同步源码和 tag：

1. **secrets 未映射**：在 job `env` 显式映射 `GITEE_USERNAME` / `GITEE_TOKEN`（当前缺失）。
2. **检测输出未写入 GITHUB_OUTPUT**：`Write-Output "secrets_configured=true"` 只打印 stdout，不会成为 `steps.check_secrets.outputs.secrets_configured`，导致 `if:` 条件恒 false。改用 `"secrets_configured=true" | Out-File -FilePath $env:GITHUB_OUTPUT -Append`。
3. **`git remote remove gitee` 报错中断**：首次运行时 remote 不存在，PowerShell 将 stderr 视为终止性错误。改用 `2>$null` 并检查 `$LASTEXITCODE`，或先 `git remote get-url gitee` 判断存在性。

同步内容保持现有逻辑：push `main` 分支与 `v*` tag。

## 错误处理

- **源码同步失败** → 工作流标红，不影响 GitHub 侧 Release。
- **Gitee Release 创建失败**（token 无效、tag 未同步、网络）→ 记录告警，不阻断 GitHub Release；两处发布解耦。
- **Gitee Release 同名重建** → 先查再删再建，幂等可重跑。

## 风险与注意

- Gitee API 创建 Release 时 `tag_name` 需在 Gitee 仓库存在，否则可能失败。由于 `sync-to-gitee` 同步 tag 与 `ci-cd` 创建 Release 可能并发执行，需在 Gitee API 步骤中处理"tag 尚未同步"的竞态：可重试（如 tag 未就绪则等待重试数次）。
- Gitee 附件大小限制与 API 速率限制：单 exe 通常数 MB~几十 MB，需关注。
- `GITEE_TOKEN` 生命周期：需在 Gitee 后台生成并妥善保管，写入 GitHub secrets。

## 测试 / 验证

1. 本地 `git push origin v2.14.0`（或 `gh workflow run` 手动触发 tag 流程）。
2. 验证 GitHub：Release `v2.14.0` 存在且含 exe 附件。
3. 验证 Gitee：
   - 仓库代码与 GitHub 同步（最新 commit、tag）。
   - Gitee Release `v2.14.0` 存在，标记为非预发布，含 exe 附件。
4. 验证 main push（beta）流程：Gitee Release 为 `vX.Y.Z-beta.SHA`，标记为预发布。
5. 重跑验证幂等：同名 Release 被替换而非报错。

## 非目标（Non-Goals）

- 不在 Gitee 引入 git 分支。
- 不构建跨平台产物（保持 Windows 单一构建）。
- 不迁移 GitHub Release 历史数据到 Gitee。
