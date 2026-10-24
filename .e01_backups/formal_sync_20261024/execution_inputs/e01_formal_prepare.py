#!/usr/bin/env python3.9
"""One-off formal sync. prepare -> external backup copy -> apply. No builds/tests/push."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile

R = Path("/home/zhaowy24/CheshireAraPULP")
F = Path("/home/zhaowy24/CheshireAra")
BF = Path("/home/zhaowy24/CheshireAra_maintenance/formal_sync_20261024")
BASE = "rebuild-baseline-20261023"
TAG = "reference-p1-p5-pass-20261024"
TB_SOURCE = "target/sim/src/tb_cheshire_soc.sv"
TB_DEST = "src/tb/src/tb_cheshire_soc.sv"
RECORD = "provenance/p1_p5_sync_20261024.json"
STEPS = [
    {
        "name": "P1",
        "candidate_commit": "26637be97e731a98ae0fd220b61f814f6a703409",
        "blobs": [
            {
                "source": ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vstu.sv",
                "before_blob": "845c81a376c693def6ffe0b985319f5a4e9fb9b8",
                "after_blob": "93afa0ed839b893898da79d95c4ba4699e6dd792"
            }
        ]
    },
    {
        "name": "P2_official",
        "candidate_commit": "7a7075a71386027b1da630bf2d8268b561957654",
        "blobs": [
            {
                "source": ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vmfpu.sv",
                "before_blob": "c125986491ac51fba722d992885c974e81d9fb08",
                "after_blob": "744dfc62efcaab74ea08be1b1e22a5e0cb84cad5"
            }
        ]
    },
    {
        "name": "P2_mask",
        "candidate_commit": "2b36bfcc68b2f2cf4b67a190804a1872262a392d",
        "blobs": [
            {
                "source": ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/masku/masku.sv",
                "before_blob": "0a48f02687548d5da30983cbc32414574f6750ba",
                "after_blob": "37b47cc1eeec8c01c34ab51c9d0d737c35627a16"
            }
        ]
    },
    {
        "name": "P2_sequencer",
        "candidate_commit": "6382e4214100c0e0de56dcd7190941cbaeebae0e",
        "blobs": [
            {
                "source": ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv",
                "before_blob": "9cd0cc405c75caa36d1b4554296ae25c786f37d1",
                "after_blob": "890e9103f14a4647e546cab1e6c9748dc4361def"
            }
        ]
    },
    {
        "name": "P3_official",
        "candidate_commit": "fa7baaa3a830f0460fecdc1c0ebf2dd444d43bda",
        "blobs": [
            {
                "source": ".bender/git/checkouts/fpu_div_sqrt_mvp-33e0a4fc0dc853c1/hdl/norm_div_sqrt_mvp.sv",
                "before_blob": "590abe969bddccabe201f2a15ae8a40d14032c95",
                "after_blob": "1d74170b5355afc7933c2ca2f8629d13a629c0db"
            }
        ]
    },
    {
        "name": "P3_mask",
        "candidate_commit": "d38bcf6925077593e6b766154d6fda205a532ed7",
        "blobs": [
            {
                "source": ".bender/git/checkouts/fpnew-ed006ec0a4178e29/src/fpnew_opgroup_multifmt_slice.sv",
                "before_blob": "f5991cbd7c46bd8f64970e8a838e3ce5db42ffdc",
                "after_blob": "90444850e9ab188b893cb2fc033446d74e437420"
            }
        ]
    },
    {
        "name": "P4_191",
        "candidate_commit": "4d1c46e3c2ecfd884202c3e86af85a2542897d93",
        "blobs": [
            {
                "source": "target/sim/src/vip_cheshire_soc.sv",
                "before_blob": "57b143d4064dd74c538d44a755221c1dc2330ad8",
                "after_blob": "3b6fcf8cbc7f25365da91c8223c0268f1e8fe91e"
            }
        ]
    },
    {
        "name": "P4_192",
        "candidate_commit": "857992bfd32a6a565d16a3b615e901f3edc6d0da",
        "blobs": [
            {
                "source": "target/sim/src/vip_cheshire_soc.sv",
                "before_blob": "3b6fcf8cbc7f25365da91c8223c0268f1e8fe91e",
                "after_blob": "e32e5410fcf4c11b7c64ad55be13ba545f28eaa8"
            }
        ]
    },
    {
        "name": "P4_adjacent",
        "candidate_commit": "ac5d74a3f32d682fe6ce73186479e1d5a564b479",
        "blobs": [
            {
                "source": "target/sim/src/vip_cheshire_soc.sv",
                "before_blob": "e32e5410fcf4c11b7c64ad55be13ba545f28eaa8",
                "after_blob": "8892c51861d2027660a2e993e65e448064d23db8"
            }
        ]
    },
    {
        "name": "P5_RTL",
        "candidate_commit": "4c0429ef96cedefc68c01ee7b88c03bab029cea7",
        "blobs": [
            {
                "source": ".bender/git/checkouts/idma-77bf7fa56d324e6a/src/frontend/reg/tpl/idma_reg.sv.tpl",
                "before_blob": "946604089b2368b68a937b1d4539b365e17f5edf",
                "after_blob": "0cfc6cd292da5e824efd1ae7e5412972bdb44141"
            },
            {
                "source": ".bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_generated.sv",
                "before_blob": "30015f02a8adb907c378ebf4ba0a3b26fef510ca",
                "after_blob": "6085b4448192897789a59c26f97fb07c5f58482d"
            },
            {
                "source": ".bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_reg32_3d_top.sv",
                "before_blob": "20ee6d8cba056b59c93236ddecfe15dd67ecd381",
                "after_blob": "65558eb42262009dbfcd0484d2ec0bef8a755fa7"
            },
            {
                "source": ".bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_reg64_2d_top.sv",
                "before_blob": "b8c2d5e5fa8fcaee5de200d58a83dbbec5f1a50a",
                "after_blob": "c702a64abe0786c0dfa259ed831727833e4f7f80"
            }
        ]
    },
    {
        "name": "P5_HAL",
        "candidate_commit": "4e2ebd52cf5206291fd088f70aeb3a198df0bec2",
        "blobs": [
            {
                "source": "sw/include/dif/dma.h",
                "before_blob": "830f9f696f1c20b517c94f68ed5db691c4a61f8b",
                "after_blob": "b75e226339fc4ed38be93c57af3f3aca204fb717"
            }
        ]
    }
]
MAP = {
    ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vstu.sv": "src/cheshire_soc/ara/hardware/src/vlsu/vstu.sv",
    ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vmfpu.sv": "src/cheshire_soc/ara/hardware/src/lane/vmfpu.sv",
    ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/masku/masku.sv": "src/cheshire_soc/ara/hardware/src/masku/masku.sv",
    ".bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv": "src/cheshire_soc/ara/hardware/src/ara_sequencer.sv",
    ".bender/git/checkouts/fpu_div_sqrt_mvp-33e0a4fc0dc853c1/hdl/norm_div_sqrt_mvp.sv": "src/cheshire_soc/fpu_div_sqrt_mvp/hdl/norm_div_sqrt_mvp.sv",
    ".bender/git/checkouts/fpnew-ed006ec0a4178e29/src/fpnew_opgroup_multifmt_slice.sv": "src/cheshire_soc/fpnew/src/fpnew_opgroup_multifmt_slice.sv",
    "target/sim/src/vip_cheshire_soc.sv": "src/tb/src/vip_cheshire_soc.sv",
    ".bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_generated.sv": "src/cheshire_soc/idma/target/rtl/idma_generated.sv",
    ".bender/git/checkouts/idma-77bf7fa56d324e6a/src/frontend/reg/tpl/idma_reg.sv.tpl": "provenance/generation/idma/src/frontend/reg/tpl/idma_reg.sv.tpl",
    "sw/include/dif/dma.h": "sw/include/dif/dma.h",
}
NEW_INPUTS = [
    "sw/tests/p1_vstu_wrap.c", "sw/tests/p2_vmfpu_order.c",
    "sw/tests/p2_vcpop_boundaries.c", "sw/tests/p2_scalar_overlap.c",
    "sw/tests/p3_div_flags.c", "sw/tests/p4_preload_bytes.c",
    "sw/tests/p5_dma_1d.spm.c", "sw/link/p4_single.ld", "sw/link/p4_multi.ld",
]
EXISTING = sorted(set(MAP.values()) | {
    TB_DEST, "sw/Makefile", "README.md", "docs/README.md",
    "docs/CONFIGURATION_AND_DEVELOPMENT.md",
    "provenance/source_manifest.json", "provenance/generation_inputs.json",
})
NEW = NEW_INPUTS + [RECORD]
EXPECTED_TESTS = {
    "p1_vstu_wrap", "p2_vmfpu_order", "p2_vcpop_boundaries", "p2_scalar_overlap",
    "p3_div_flags", "p3_mask_matrix", "p4_01", "p4_02", "p4_03",
    "p4_04", "p4_05", "p4_06", "p5_dma_1d", "p5_dma_sequence",
}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(R), *args])


def gitstr(*args):
    return git(*args).decode().strip()


def blob(ref, path):
    return git("show", ref + ":" + path)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def write_json(path, value):
    # Backup-area state only; never writes arbitrary F inputs.
    path.write_bytes(json_bytes(value))


def metadata(path):
    st = path.lstat()
    mode = stat.S_IMODE(st.st_mode)
    if stat.S_ISLNK(st.st_mode):
        target = os.readlink(str(path))
        return {"kind": "symlink", "mode": mode, "target": target,
                "sha256": digest(os.fsencode(target))}
    need(stat.S_ISREG(st.st_mode), "Unsupported input type: " + str(path))
    return {"kind": "file", "mode": mode, "size": st.st_size,
            "sha256": digest(path.read_bytes())}


def inventory():
    """Inventory inputs without following symlink dirs or reading output trees."""
    result = {}
    for root, dirs, files in os.walk(str(F), followlinks=False):
        for name in list(dirs):
            p = Path(root) / name
            rel = p.relative_to(F).as_posix()
            if rel in ("sim/work", "sw/build"):
                dirs.remove(name)
            elif p.is_symlink():
                dirs.remove(name)
                result[rel] = metadata(p)
        for name in files:
            p = Path(root) / name
            result[p.relative_to(F).as_posix()] = metadata(p)
    return result


def safe_target(rel):
    p = F / rel
    need(not Path(rel).is_absolute() and ".." not in Path(rel).parts,
         "Unsafe relative path: " + rel)
    need(p.parent.resolve() == p.parent, "Symlinked parent: " + str(p))
    need(not p.is_symlink(), "Symlink target: " + str(p))
    return p


def reference_state():
    need(R.resolve() == R and F.resolve() == F, "Root path is symlinked")
    head = gitstr("rev-parse", "HEAD")
    base = gitstr("rev-parse", BASE + "^{commit}")
    tag = gitstr("rev-parse", TAG + "^{commit}")
    git("merge-base", "--is-ancestor", tag, head)
    need(not gitstr("status", "--porcelain=v1", "--untracked-files=all"),
         "R working tree not clean")
    remote = gitstr("ls-remote", "--exit-code", "personal", "refs/heads/main")
    need(remote.split() == [head, "refs/heads/main"],
         "personal/main does not equal R HEAD")
    return {"head": head, "baseline": base, "passed_tag": TAG, "passed_commit": tag,
            "remote_main": head}


def resolve_steps(reference):
    """Locate actual R commits via exact before/after blobs, not commit titles."""
    commits = gitstr("rev-list", "--reverse", reference["baseline"] + ".." +
                     reference["passed_commit"]).splitlines()
    resolved = []
    last_index = -1
    for spec in STEPS:
        paths = [a["source"] for a in spec["blobs"]]
        hits = []
        for index, commit in enumerate(commits):
            parents = gitstr("rev-list", "--parents", "-n", "1", commit).split()
            if len(parents) != 2:
                continue
            changed = set(gitstr("diff-tree", "--no-commit-id", "--name-only",
                                "-r", commit).splitlines())
            if not set(paths) <= changed:
                continue
            if all(gitstr("rev-parse", parents[1] + ":" + a["source"]) == a["before_blob"]
                   and gitstr("rev-parse", commit + ":" + a["source"]) == a["after_blob"]
                   for a in spec["blobs"]):
                hits.append((index, commit, parents[1]))
        need(len(hits) == 1, "Expected one R commit for " + spec["name"] + ": " + repr(hits))
        index, commit, parent = hits[0]
        need(index > last_index, "Unexpected R repair ordering: " + spec["name"])
        last_index = index
        resolved.append(dict(spec, r_commit=commit, r_parent=parent))
    return resolved


def checked_reference_file(reference, rel):
    data = blob(reference["passed_commit"], rel)
    p = R / rel
    need(p.is_file() and not p.is_symlink(), "Non-regular R input: " + rel)
    need(p.read_bytes() == data, "Actual R input differs from passed tag: " + rel)
    return data


def transformed_tb(reference, old_f):
    base = blob(reference["baseline"], TB_SOURCE)
    current = checked_reference_file(reference, TB_SOURCE)
    selector = (
        b"  /// The selected simulation configuration from the \x60tb_cheshire_pkg\x60.\n"
        b"  parameter int unsigned SelectedCfg = 32'd0,\n"
    )
    connection = b"    .SelectedCfg  (SelectedCfg),\n"
    need(base.count(selector) == 1 and base.count(connection) == 1,
         "Unexpected R baseline SelectedCfg layout")
    expected_f = base.replace(selector, b"").replace(connection, b"")
    need(old_f == expected_f, "F TB contains changes beyond known SelectedCfg removal")
    ending = b"endmodule\n"
    need(base.endswith(ending) and current.endswith(ending), "Unexpected TB ending")
    prefix = base[:-len(ending)]
    need(current.startswith(prefix), "R TB changed original body outside appended monitor block")
    delta = current[len(prefix):-len(ending)]
    need(b"P1_VSTU_GATE" in delta and b"P5_DMA_MONITOR" in delta, "Missing TB controls")
    adjusted = re.sub(rb"fix\.dut\.(?=gen_)", b"fix.dut.i_soc.", delta)
    need(not re.search(rb"fix\.dut\.(?!i_soc\.)", adjusted),
         "Unmapped direct DUT reference in monitor block")
    return old_f[:-len(ending)] + adjusted + ending


def transformed_make(reference, old_f):
    r = checked_reference_file(reference, "sw/Makefile").decode()
    lines = [line for line in r.splitlines()
             if re.match(r"^\$\(eval \$\(call direct_test,p[1-5]", line)]
    names = [re.match(r"^\$\(eval \$\(call direct_test,([^,]+),", x).group(1)
             for x in lines]
    need(len(lines) == 14 and set(names) == EXPECTED_TESTS, "Unexpected R test targets")
    text = old_f.decode()
    need(not any(re.search(r"\bdirect_test," + re.escape(n) + ",", text)
                 for n in names), "Maintenance tests already registered in F")
    marker = ".PHONY: all\n"
    need(text.count(marker) == 1, "Unexpected F Make all target layout")
    return text.replace(marker, "\n".join(lines) + "\n\n" + marker).encode()


def make_operations(reference, steps):
    """Build all changes in memory; each operation checks its exact preimage."""
    current = {rel: safe_target(rel).read_bytes() for rel in EXISTING}
    initial = dict(current)
    operations = []
    for step in steps:
        changes = []
        for a in step["blobs"]:
            src = a["source"]
            if src not in MAP:
                continue
            dst = MAP[src]
            before = blob(step["r_parent"], src)
            after = blob(step["r_commit"], src)
            need(current[dst] == before, "F preimage conflict at " + step["name"] + ": " + dst)
            changes.append({"destination": dst, "source": src,
                            "before": before, "after": after,
                            "mode": metadata(safe_target(dst))["mode"]})
            current[dst] = after
        need(changes, "Empty mapped repair step")
        operations.append({"name": step["name"], "r_commit": step["r_commit"],
                           "r_parent": step["r_parent"], "changes": changes})
    for src, dst in MAP.items():
        need(current[dst] == checked_reference_file(reference, src),
             "Unselected follow-on R production change: " + src)
    tests = []
    for rel in NEW_INPUTS:
        p = safe_target(rel)
        need(not p.exists(), "New input already exists: " + rel)
        mode_word = gitstr("ls-tree", reference["passed_commit"], "--", rel).split()[0]
        need(mode_word in ("100644", "100755"), "Unexpected source mode: " + rel)
        tests.append({"destination": rel, "source": rel, "before": None,
                      "after": checked_reference_file(reference, rel),
                      "mode": int(mode_word[-3:], 8)})
    tests += [
        {"destination": TB_DEST, "source": TB_SOURCE, "before": initial[TB_DEST],
         "after": transformed_tb(reference, initial[TB_DEST]),
         "mode": metadata(F / TB_DEST)["mode"]},
        {"destination": "sw/Makefile", "source": "sw/Makefile",
         "before": initial["sw/Makefile"],
         "after": transformed_make(reference, initial["sw/Makefile"]),
         "mode": metadata(F / "sw/Makefile")["mode"]},
    ]
    operations.append({"name": "test_inputs_and_wrapper_paths",
                       "r_commit": reference["passed_commit"], "changes": tests})
    return operations


def assert_baseline(reference):
    for src, dst in MAP.items():
        need(safe_target(dst).read_bytes() == blob(reference["baseline"], src),
             "F source differs from R rebuild baseline: " + dst)
    for rel in EXISTING:
        need(metadata(safe_target(rel))["kind"] == "file", "Non-regular backup target: " + rel)
    for rel in NEW:
        need(not safe_target(rel).exists(), "Expected new path already exists: " + rel)


def prepare():
    reference = reference_state()
    steps = resolve_steps(reference)
    assert_baseline(reference)
    make_operations(reference, steps)
    need(not BF.exists(), "Backup directory already exists; inspect it, do not overwrite")
    before = inventory()
    BF.mkdir(parents=True)
    write_json(BF / "all_inputs_before.json", before)
    selected = {rel: before[rel] for rel in EXISTING}
    archive = BF / "before.tar"
    with tarfile.open(str(archive), "w") as tar:
        for rel in EXISTING:
            tar.add(str(F / rel), arcname=rel, recursive=False)
    restore = BF / "restore_check"
    restore.mkdir()
    with tarfile.open(str(archive), "r") as tar:
        members = tar.getmembers()
        need(sorted(m.name for m in members) == EXISTING, "Backup member mismatch")
        for member in members:
            need(member.isfile() and member.name in selected, "Unexpected archive member")
            dst = restore / member.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source:
                dst.write_bytes(source.read())
            os.chmod(str(dst), member.mode)
            need(metadata(dst) == selected[member.name], "Restore check failed: " + member.name)
    need(inventory() == before, "F changed while backup was created")
    meta = {"status": "prepared_not_applied", "reference": reference, "steps": steps,
            "existing": selected, "new_paths": NEW, "all_inputs_count": len(before),
            "backup": str(archive), "backup_sha256": digest(archive.read_bytes()),
            "restore_checked_files": len(EXISTING), "restore_check": str(restore),
            "source_map": MAP,
            "skipped_unextracted_sources": [a["source"] for step in STEPS for a in step["blobs"]
                                           if a["source"] not in MAP]}
    write_json(BF / "prepared.json", meta)
    print(json.dumps({"backup": str(archive), "sha256": meta["backup_sha256"],
                      "restore_checked_files": len(EXISTING),
                      "next": "Copy backup and metadata to local storage, verify SHA, then call apply separately."}))


def apply_change(change):
    rel = change["destination"]
    p = safe_target(rel)
    before, after, mode = change["before"], change["after"], change["mode"]
    need(p.parent.is_dir(), "Missing existing parent for " + rel)
    if before is None:
        need(not p.exists(), "Refusing to overwrite new-file collision: " + rel)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    else:
        need(metadata(p)["mode"] == mode, "Mode changed before apply: " + rel)
        flags = os.O_RDWR | os.O_NOFOLLOW
    fd = os.open(str(p), flags, mode)
    with os.fdopen(fd, "wb" if before is None else "r+b") as stream:
        if before is not None:
            need(stream.read() == before, "Preimage changed at write time: " + rel)
            stream.seek(0)
        stream.write(after)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())
        if before is None:
            os.fchmod(stream.fileno(), mode)
    need(p.read_bytes() == after and metadata(p)["mode"] == mode, "Write verification failed: " + rel)


def apply(args):
    need(args.local_backup_sha256 and args.local_backup_location,
         "apply requires local backup verification digest and local backup location")
    prepared = json.loads((BF / "prepared.json").read_text())
    need(not (BF / "apply_journal.json").exists(), "An apply attempt already exists; inspect before recovery")
    sha = digest((BF / "before.tar").read_bytes())
    need(sha == prepared["backup_sha256"] == args.local_backup_sha256,
         "Backup SHA mismatch or no verified local copy")
    reference = reference_state()
    need(reference == prepared["reference"], "R refs changed after prepare")
    before = json.loads((BF / "all_inputs_before.json").read_text())
    need(inventory() == before, "F inputs changed since prepare")
    assert_baseline(reference)
    need(resolve_steps(reference) == prepared["steps"], "R step mapping changed")
    operations = make_operations(reference, prepared["steps"])
    patchdir = BF / "patches"
    patchdir.mkdir()
    for index, op in enumerate(operations, 1):
        patch = ""
        for change in op["changes"]:
            rel = change["destination"]
            patch += "".join(difflib.unified_diff(
                [] if change["before"] is None else change["before"].decode().splitlines(True),
                change["after"].decode().splitlines(True),
                fromfile="/dev/null" if change["before"] is None else "a/" + rel,
                tofile="b/" + rel))
        (patchdir / ("%02d_%s.patch" % (index, op["name"]))).write_text(patch)
    journal = {"status": "applying", "reference": reference, "local_backup_verified_sha256": sha,
               "local_backup_location": args.local_backup_location,
               "completed_steps": [], "completed_files": []}
    write_json(BF / "apply_journal.json", journal)
    changed = set()
    try:
        for op in operations:
            for change in op["changes"]:
                apply_change(change)
                changed.add(change["destination"])
                journal["completed_files"].append({
                    "step": op["name"], "destination": change["destination"],
                    "before_sha256": None if change["before"] is None else digest(change["before"]),
                    "after_sha256": digest(change["after"]), "mode": change["mode"]})
                write_json(BF / "apply_journal.json", journal)
            journal["completed_steps"].append({k: v for k, v in op.items() if k != "changes"})
            write_json(BF / "apply_journal.json", journal)
        summary = {
            "status": "source_synchronized_pending_formal_validation",
            "reference": reference, "production_steps": prepared["steps"],
            "source_map": MAP, "backup_directory": str(BF),
            "backup_sha256": sha, "new_paths": NEW,
            "changes": journal["completed_files"],
            "skipped_unextracted_sources": prepared["skipped_unextracted_sources"],
            "pending": ["Update source_manifest, generation_inputs and three user docs",
                        "Rebuild and run directed/cumulative/peripheral regressions in F",
                        "Verify unaffected inputs and save final evidence"],
            "configuration_wrapper_and_existing_compile_start_unchanged": True,
            "tests_run_by_this_program": False, "push_by_this_program": False,
        }
        apply_change({"destination": RECORD, "before": None,
                      "after": json_bytes(summary), "mode": 0o644})
        changed.add(RECORD)
        after = inventory()
        need(set(after) == set(before) | set(NEW), "Unexpected F input addition/removal")
        for rel in set(before) - changed:
            need(after[rel] == before[rel], "Protected input changed: " + rel)
        for src, dst in MAP.items():
            need((F / dst).read_bytes() == checked_reference_file(reference, src),
                 "Final production mismatch: " + dst)
        write_json(BF / "all_inputs_after_apply.json", after)
        journal["status"] = "source_applied_not_tested"
        journal["after"] = {rel: after[rel] for rel in sorted(changed)}
        write_json(BF / "apply_journal.json", journal)
        print(json.dumps({"status": journal["status"], "changed_files": len(changed),
                          "journal": str(BF / "apply_journal.json")}))
    except Exception as exc:
        journal["status"] = "failed_preserve_progress"
        journal["error"] = repr(exc)
        write_json(BF / "apply_journal.json", journal)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "apply"))
    parser.add_argument("--local-backup-sha256")
    parser.add_argument("--local-backup-location",
                        help="Location of verified local backup supplied by coordinating Agent")
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        apply(args)


if __name__ == "__main__":
    main()

