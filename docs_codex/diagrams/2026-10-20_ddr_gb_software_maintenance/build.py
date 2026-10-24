#!/usr/bin/env python3
"""Revise the three affected figures using the existing industrial helpers."""
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
D = Path(__file__).resolve().parent
OLD = D.parent / "2026-10-20_ddr_gb_coherence_v1"
SIMPLE = D.parent / "2026-10-20_ddr_gb_simple_timeline"
spec = importlib.util.spec_from_file_location("coherence_v1", OLD / "build.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def system():
    f = old.system()
    removed = {"maint", *[a["id"] for a in f.arrows if a["id"].startswith("maint-")]}
    f.parts = [p for p in f.parts
               if not any(f'id="{k}"' in p or f'data-owner="{k}"' in p for k in removed)]
    f.arrows = [a for a in f.arrows if a["id"] not in removed]
    f.boxes.pop("maint")
    replacements = {
        "SoC v1：DDR–GB 数据路径与范围维护": "SoC v1：软件触发的 DDR–GB 缓存维护",
        "CPU / Ara2 共享 M5；F0–F3 共享压缩前端；控制箭头表示逻辑职责，接口编码待实现。":
            "输入：FENCE + LLC 全量 flush；输出：软件配置范围，硬件失效 L1D / LLC。",
        "蓝：AXI 请求 / 返回（F2 仅写，F3 仅读）    绿：GB 局部访问 / 像素流    紫：软件命令、维护、准入与确认":
            "蓝：AXI 请求 / 返回（F2 仅写，F3 仅读）    绿：GB / 像素流    紫：MMIO 命令 / 状态、缓存维护 / 完成",
        "GB 本地交接管理使用权；DDR 同步涵盖缓存、共享前端与控制器。未画出的外设 / 配置 / eMMC 路径沿用 v1。":
            "软件等待缓存维护与数据可见，再启动搬运或消费结果；虚线框为待扩展维护逻辑，数据连接沿用 v1。",
    }
    for a, b in replacements.items():
        f.parts = [p.replace(a, b) for p in f.parts]
    f.box("mmio", 800, 650, 620, 55, "既有寄存器总线 / MMIO", fill="agent")
    f.box("maint", 800, 740, 900, 125, "缓存维护控制（待扩展）",
          ["范围寄存器 / 行地址发生", "排空与失效状态机 / 完成与错误"], fill="agent", dashed=True)
    f.arrow("xbar-mmio", [(950, 590), (950, 650)], "control", both=True, start="xbar", end="mmio")
    f.arrow("mmio-maint", [(1250, 705), (1250, 740)], "control", both=True, start="mmio", end="maint")
    f.arrow("maint-cpu", [(800, 765), (760, 765), (760, 690), (40, 690), (40, 240), (80, 240)],
            "control", both=True, start="maint", end="cpu")
    f.arrow("maint-llc", [(800, 830), (510, 830)], "control", both=True, start="maint", end="llc")
    return f


def ownership():
    f = old.revised_ownership()
    mapping = {
        "输出失效 / 回填协调": "FENCE 推进到 LLC",
        "LLC 范围维护": "LLC 全量 flush",
        "输入：clean": "输入 / 输出旧写一起保存",
        "输出：clean + invalidate": "写回并失效，等待结束",
        "汇合缓存维护确认": "软件核对响应与错误",
        "输入的干净副本可保留；输出预清理保护未覆盖字节，预失效清除旧副本。":
            "L1D 干净副本可保留；一次全量写回保护输出未覆盖字节，此后保持范围使用约定。",
        "L1D + LLC": "LLC → L1D",
        "请求输出范围同步": "MMIO 提交输出范围",
        "紫色箭头：阶段顺序与完成依赖    绿色箭头：设备搬运与计算阶段    维护动作以目标物理范围为单位":
            "紫：软件排序与缓存完成依赖    绿：搬运与计算    首版全量写回，写后按输出范围失效",
    }
    from html import escape
    for a, b in mapping.items():
        f.parts = [p.replace(escape(a), escape(b)) for p in f.parts]
    return f


def timeline():
    # Execute the existing small drawing source with only approved label edits.
    source = (SIMPLE / "build.py").read_text()
    source = source.replace("先排空旧事务，再清理输入、清理并失效输出",
                            "FENCE 排空写缓冲 → LLC 全量 flush 并等待")
    source = source.replace("确认设备端口可见，允许启动搬运",
                            "同时保存输出区旧写；确认设备端口可见后启动搬运")
    source = source.replace("确认写回成功且 CPU 端口可见",
                            "确认结果可见；软件提交输出范围，启动缓存失效")
    source = source.replace("处理相关回填，再失效 L1D／LLC 输出副本",
                            "处理旧回填，完成 LLC／L1D 失效后交还 CPU")
    env = {"__file__": str(D / "build.py"), "__name__": "timeline_revision"}
    exec(compile(source, str(SIMPLE / "build.py"), "exec"), env)
    return env["layout"]


if __name__ == "__main__":
    out = D / "figures"
    out.mkdir(exist_ok=True)
    layouts = [system().save(out), ownership().save(out), timeline()]
    (out / "layout.json").write_text(json.dumps(layouts, ensure_ascii=False, indent=2) + "\n")
    print("Updated system, ownership, and five-stage timeline")
