# L01-S 本轮证据

- `input.json` / `before/`：本任务修改前版本、git状态及7份源正文原件。其他路径的总保护由主管维护。
- `actions-before.md`：修改前段落动作账本。
- `sources.json`：37个定向来源哈希、符号/主题及官方在线适用性。源文件只读。
- `check_content.py`：只读检查正文唯一ID、原锚点、原图引用、本地链接/锚点、几个关键阅读顺序和算法期望总和。
- `content-check-initial.json`、`content-check-final.json`、`content-check-release.json`：各阶段独立输出；不覆盖旧记录。release为本任务最新结果。
- `diff-check.txt`：git diff --check退出0，无输出。

重现只读检查（从仓库根执行，输出到新的文件）：

```sh
python3 docs_codex/learning/evidence/system-implementation-20261008/software/check_content.py
```

Python 3.13.5。没有生成站点、运行浏览器、构建目标软件或RTL、仿真/综合/板测。最终公共验收由主管串行完成，不能将源检查报告扩大成生成站点或目标运行通过。

定位来源时曾尝试不存在的 `util/gdb_run.sh`、`util/openocd.sh`（只读cat失败），随后用rg确定实际OpenOCD tcl入口；不存在的路径没有写入教材命令。两个ISA官方网页读取失败，改用本地随附官方说明并核消费者，详见sources.json。
