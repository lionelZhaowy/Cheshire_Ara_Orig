#!/usr/bin/env python3
"""Install this skill into a fresh personal location using a supplied wheelhouse."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("Use install_windows.ps1 on Windows")
    source = Path(__file__).resolve().parent.parent
    target = Path.home()/".codex/skills/svg-pptx-diagrams"
    discovery = Path.home()/".agents/skills/svg-pptx-diagrams"
    if target.exists() or target.is_symlink() or discovery.exists() or discovery.is_symlink():
        parser.error("Target already exists; inspect it before updating")
    wheels = list(args.wheelhouse.resolve().glob("pip-*.whl"))
    if len(wheels) != 1:
        parser.error("Supply exactly one pip wheel along with requirement wheels")
    target.mkdir(parents=True)
    for entry in ["SKILL.md","requirements.txt","agents","scripts","references","assets"]:
        src, dst = source/entry, target/entry
        if src.is_dir():
            shutil.copytree(src,dst,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        else:
            shutil.copy2(src,dst)
    subprocess.run([sys.executable,"-m","venv","--without-pip",str(target/".venv")],check=True)
    python = target/".venv/bin/python"
    seed_env = dict(os.environ, PYTHONPATH=str(wheels[0]), PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([str(python),"-m","pip","install","--no-index","--find-links",
                    str(args.wheelhouse.resolve()),"pip","-r",str(target/"requirements.txt")],
                    env=seed_env,check=True)
    discovery.parent.mkdir(parents=True,exist_ok=True)
    discovery.symlink_to(target,target_is_directory=True)
    check_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([str(python),str(target/"scripts/test_svg_to_pptx.py"),"-v"],env=check_env,check=True)
    out = target/"validation-linux"
    subprocess.run([sys.executable,str(target/"scripts/run.py"),"--input",
                    str(target/"assets/example.svg"),"--out-dir",str(out)],env=check_env,check=True)
    report = {"target":str(target),"discovery":str(discovery),"python":str(python),
              "behavioral_checks_passed":True,"native_export_passed":True,
              "powerpoint_tested":False,"output":str(out),"offline_install":True}
    (target/"installation_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
