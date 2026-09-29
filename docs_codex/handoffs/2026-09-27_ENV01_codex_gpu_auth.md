# ENV01 / GPU Codex 登录缓存迁移

## 基本信息

- 日期：2026-09-27。
- 用户授权：分析并将本人 WSL VSCode Codex 登录状态迁移到本人 GPU 服务器账号。
- 状态：认证文件迁移完成；远端 CLI 登录状态检查通过；VSCode 界面及实际模型请求待验证。
- 输入提交：`4f240258ca683913b7e17949aff23139bff981f1`；执行前 `git status --short` 为空。
- 范围：用户级 Codex 认证文件及本交接；未修改 RTL、构建、依赖或共享项目状态。

## 本轮结果与改动

- WSL 的默认 Codex 目录存在 ChatGPT 类型认证缓存，文件权限为 600；没有输出凭据内容。
- WSL 直接 SSH 检查超时；Windows TCP22 连通，Windows OpenSSH 使用已有配置成功登录 GPU。
- GPU 扩展及进程使用 `/home/zhaowenyao24/.codex`，迁移前没有 `auth.json`；未发现显式认证存储/登录方式限制配置行。
- 使用 Windows OpenSSH，将 WSL 认证缓存以标准输入传送给远端 Python，通过权限为 600 的临时文件和硬链接创建最终文件；若目标已存在则停止，未覆盖既有文件。
- 目标：GPU 用户目录的 `.codex/auth.json`，未复制配置、会话、插件或整个 `.codex`。
- 新增本交接，未提交。凭据只保存在用户认证目录，不进入仓库或日志。

## 验证证据

- 目标文件权限：600；传输内容完整性检查：True；安装退出码：0。
- 远端命令：`/home/zhaowenyao24/.vscode-server/extensions/openai.chatgpt-26.5901.22334-linux-x64/bin/linux-x86_64/codex login status`。
- 返回：`Logged in using ChatGPT`，退出码 0。
- 官方依据：https://learn.chatgpt.com/docs/auth ，Login caching / Fallback: Authenticate locally and copy your auth cache。
- 浏览器 localhost 回调未到达远端是符合现象的推断，未复现原始登录流程，不能当作根因已证实。
- 未执行实际模型请求、VSCode 窗口重载、工程编译/仿真/板测。

## 下一步

1. 在连接 GPU 的 VSCode 窗口执行 `Developer: Reload Window`，检查 Codex 登录界面。
2. 发起简单对话验证网络和服务端认证；如果失败，记录脱敏错误继续诊断。
3. 如需以后在 GPU 独立重新登录，可使用官方设备码登录或 SSH 转发 localhost:1455 回调。

本任务属于个人开发环境维护，不改变硬件项目事实或既有任务状态，无需 C00 更新项目状态表。
