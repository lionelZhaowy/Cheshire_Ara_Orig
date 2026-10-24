# CheshireAra 本次局部同步的回退

本说明仅用于 `formal_sync_20261024` 已完成版本。执行前停止本工程的新构建/修改，保留现有日志；以下命令会先核对全部27个涉及文件的结束哈希/权限，另存当前27文件，再恢复17旧文件并移除10新增文件。任何并发修改都应停止并人工合并，不可绕过检查。不会清理输出、恢复Bender或修改参考工程。

```bash
/usr/bin/python3.9 - <<'PY'
from pathlib import Path
import json, hashlib, stat, tarfile, os, datetime
F=Path('/home/zhaowy24/CheshireAra')
B=Path('/home/zhaowy24/CheshireAra_maintenance/formal_sync_20261024')
p=json.loads((B/'prepared.json').read_text())
a=json.loads((B/'final_after.json').read_text())
def meta(f):
    assert f.is_file() and not f.is_symlink(), f
    return {'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mode':stat.S_IMODE(f.stat().st_mode)}
paths=list(p['existing'])+p['new_paths']
for r in paths:
    assert meta(F/r)=={k:a[r][k] for k in ('sha256','mode')}, ('changed since validation',r)
assert hashlib.sha256((B/'before.tar').read_bytes()).hexdigest()==p['backup_sha256']
with tarfile.open(B/'before.tar','r') as t:
    assert sorted(m.name for m in t.getmembers())==sorted(p['existing'])
    old={m.name:(t.extractfile(m).read(),m.mode) for m in t.getmembers() if m.isfile()}
assert set(old)==set(p['existing'])
for r,(data,mode) in old.items():
    assert hashlib.sha256(data).hexdigest()==p['existing'][r]['sha256'] and mode==p['existing'][r]['mode']
saved=B/('before_rollback_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.tar')
assert not saved.exists()
with tarfile.open(saved,'x') as t:
    for r in paths: t.add(F/r,arcname=r,recursive=False)
for r,(data,mode) in old.items():
    assert meta(F/r)=={k:a[r][k] for k in ('sha256','mode')}, r
    (F/r).write_bytes(data); os.chmod(F/r,mode)
for r in p['new_paths']:
    assert meta(F/r)=={k:a[r][k] for k in ('sha256','mode')}, r
    (F/r).unlink()
for r in p['existing']:
    assert meta(F/r)=={k:p['existing'][r][k] for k in ('sha256','mode')}, r
assert all(not (F/r).exists() for r in p['new_paths'])
print('Restored 17 old files; removed 10 listed additions; preserved pre-rollback files:',saved)
PY
```

回退后的重新构建须使用新输出目录。`before.tar`已实际解包并逐文件验证；上述完整回退命令为备用操作，本次通过后不执行回退。
