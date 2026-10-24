# Reproduce the fixed source's one-round sub_per_hash wiring; compare to sampled RTL before using.
import json
seeds=[(299034753,4094834),(19921030,995713),(294388,65146511)]
def hashes(data):
 out=[]
 for pk,xk in seeds:
  n=16;perm=[0]*n;r=(2147483629*pk+2147483587)%(2**31-1)
  for i in range(n):
   idx=0
   if i:r=(2147483629*r+2147483587)%(2**31-1);idx=r%i
   if i!=idx:perm[i]=perm[idx];perm[idx]=i
  r=(1664525*xk+1013904223)%2**32;h=0
  for i in range(n):
   r=(1664525*r+1013904223)%2**32;bit=0
   for j in range(3):
    r=(1664525*r+1013904223)%2**32;bit^=(data>>perm[r%n])&1
   if i<6:h|=bit<<i
  out.append(h)
 return out
for x in [0x3c04,0x3c10]:
 h=hashes(x);print(hex(x),h,hex(sum(1<<b for b in set(h))))
