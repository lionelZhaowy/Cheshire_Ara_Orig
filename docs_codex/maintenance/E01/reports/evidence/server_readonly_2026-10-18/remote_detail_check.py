import pathlib,re,subprocess,hashlib,os,json
p=pathlib.Path.home()/"Desktop/mycheshire_24"
for rel in ["src/tb/src/tb_cheshire_pkg.sv","src/tb/src/tb_cheshire_soc.sv"]:
 f=p/rel; print("FILE",rel)
 for i,line in enumerate(f.read_text().splitlines(),1): print(str(i)+": "+line)
print("FILELIST_INTEGRITY_FROM_SIM_WORK")
lines=(p/"src/filelist.f").read_text().splitlines(); sources=[]; inc=[]; other=[]
for l in lines:
 l=l.strip()
 if not l or l.startswith("//"): continue
 if l.startswith("+incdir+"): inc.extend(l[len("+incdir+"):].split("+"))
 elif l.startswith(("+","-")): other.append(l)
 else:sources.append(l)
missing=[f for f in sources+inc if not (p/"sim/work"/f).exists()]
print(json.dumps({"sources":len(sources),"unique_sources":len(set(sources)),"includes":len(inc),"other":other,"missing":missing}))
print("SELECTED_SOURCE_HASHES")
for rel in ["src/filelist.f","src/tb/src/elfloader.cpp","src/tb/src/tb_cheshire_pkg.sv","src/tb/src/vip_cheshire_soc.sv","src/tb/src/fixture_cheshire_soc.sv","src/cheshire_soc/cheshire_top/cheshire_pkg.sv","src/cheshire_soc/cheshire_top/cheshire_soc.sv"]:
 f=p/rel
 if f.exists(): print(hashlib.sha256(f.read_bytes()).hexdigest(),rel)
print("CHESHIRE_TOP_FILES")
for root,dirs,files in os.walk(str(p/"src/cheshire_soc/cheshire_top")):
 if len(pathlib.Path(root).relative_to(p/"src/cheshire_soc/cheshire_top").parts)>1: dirs[:]=[]; continue
 print(os.path.relpath(root,str(p)), sorted(files))
print("LIBRARY_AND_HEADER_PRESENCE")
for s in ["/opt/riscv/riscv64-unknown-elf/lib/libc.a","/opt/riscv/lib/gcc/riscv64-unknown-elf/13.2.0/libgcc.a","/opt/riscv/riscv64-unknown-elf/include/newlib.h","/opt/riscv/lib/gcc/riscv64-unknown-elf/13.2.0/include/riscv_vector.h"]:
 f=pathlib.Path(s); print(s, f.stat().st_size if f.exists() else "ABSENT")
 if f.exists() and f.name=="newlib.h":
  for l in f.read_text().splitlines():
   if "VERSION" in l: print(l)
for option in ["-print-prog-name=as","-print-prog-name=ld"]:
 r=subprocess.run(["/opt/riscv/bin/riscv64-unknown-elf-gcc",option],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,timeout=10)
 print(option,"rc",r.returncode,r.stdout.strip())
print("VCS_VERSION_QUERY")
r=subprocess.run(["vcs","-full64","-ID"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,timeout=30)
print("rc",r.returncode)
for line in r.stdout.splitlines():
 if not re.search(r'license|SNPSLMD|LM_LICENSE|server.*@',line,re.I): print(line)
