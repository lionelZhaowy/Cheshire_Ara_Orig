#!/usr/bin/env python3
"""Page 4 only: unified configuration and explicit shared-storage channels."""
import argparse,json,subprocess
from pathlib import Path
from revise_page4_layout import make,source_colours,resolve_colour,revise,config_tag,MATCH

D=Path(__file__).resolve().parent
CONFIG=[
 ('pll',['PLL / 时钟','复位']),('ddr-controller',['DDR','Controller']),
 ('ddr-phy',['DDR','PHY']),('lvds-rx',['LVDS','RX']),('isp',['ISP']),
 ('npu',['NPU','计算']),('gb-mover',['NPU / GB','搬运']),
 ('frame-dma',['帧写入','DMA']),('global-buffer',['GB','管理']),
 ('emmc-host',['eMMC Host','/ DMA']),('roi-scheduler',['ROI 任务','/ 调度']),
 ('front-adapt',['前端公共','控制']),('roi-vdma',['帧输出','VDMA']),
 ('lvds-tx',['LVDS','TX']),('compressor',['压缩器']),('decompressor',['解压器'])]

def revised(fills,theme):
    d=make(fills,theme)
    def remove_objects(ids):
        d.regions[:]=[b for b in d.regions if b['id'] not in ids]
        d.boxes[:]=[b for b in d.boxes if b['id'] not in ids]
        d.texts[:]=[t for t in d.texts if t['owner'] not in ids and t['id'] not in ids]
    def remove_edges(ids):d.edges[:]=[e for e in d.edges if e['id'] not in ids]
    def edge(id):return next(e for e in d.edges if e['id']==id)
    def box(id):return next(b for b in d.boxes+d.regions if b['id']==id)
    def text(id):return next(t for t in d.texts if t['id']==id)

    # Keep the existing C10/C3 badges clear of their neighbouring descriptions.
    text('emmc-host-t1')['x']-=20
    text('ddr-phy-t1')['x']-=20

    # All RegExt configuration groups occur exactly once on the bottom row.
    remove_objects({f'{prefix}C{i}' for i in range(1,13) for prefix in ['config-','reg-badge-']})
    remove_edges({'new-reg-config','regext-old-config','old-config-trunk'}|
                 {f'old-cfg-C{i}' for i in range(1,10)}|{f'cfg-C{i}' for i in [10,11,12]})
    box('reg-region')['h']=520
    width=(3255-15*14)/16;first=71.25+width/2;last=3326.25-width/2
    d.dots[:]=[(x,1838.1 if (x,y)==(1785,1853.1) else y,k) for x,y,k in d.dots]
    d.edge('regext-config','reg-ext','config-trunk',[(1726.25,1569),(1785,1569),(1785,1838.1)],'cfg',arrow=False)
    d.edge('config-trunk','config-trunk','config-trunk',[(first,1838.1),(last,1838.1)],'cfg',arrow=False)
    cfgfill=resolve_colour(fills['config-C1'],theme)
    for i,(_,lines) in enumerate(CONFIG,1):
        x=71.25+(i-1)*(width+14);id=f'config-C{i}'
        fill=resolve_colour(fills[id],theme) if i<=9 else cfgfill
        d.rect(id,x,1862.1,width,116,fill,dash=True)
        config_tag(d,f'C{i}',x+7,1867.1)
        yy=[1929.1,1964.1] if len(lines)==2 else [1947.1]
        for j,(s,y) in enumerate(zip(lines,yy)):d.text(id+f'-title-{j}',x+width/2,y,s,30,True,owner=id)
        d.edge(f'cfg-C{i}','config-trunk',id,[(x+width/2,1838.1),(x+width/2,1862.1)],'cfg')
        d.dot(x+width/2,1838.1,'cfg')

    # Four upstream contexts share a service fabric. AR/AW and B bypass codecs.
    oldfront={'compression-front','front-adapt','compressor','decompressor','plain-bypass','metadata','front-route','badge-C12'}|{f'front-F{i}' for i in range(4)}
    remove_objects(oldfront)
    remove_edges({e['id'] for e in d.edges if e['src'] in oldfront and e['dst'] in oldfront}|
                 {f'front-ddr-{i}' for i in range(4)})
    d.rect('compression-front',1810,1134,1120,406,'green',True,True)
    ports=[1950,2225,2500,2775]
    for i,(x,who) in enumerate(zip(ports,['LLC','GB 搬运','帧写','帧读'])):
        d.block(f'front-F{i}',x-85,1116,170,36,[f'F{i} · {who}'],'white',[22.5])
        d.edge(f'front-input-{i}',f'front-F{i}','front-adapt',[(x,1152),(x,1168)],arrow=False)
    d.block('front-adapt',1830,1168,1080,52,['共享压缩前端 · 四口区域选择 / 事务跟踪'],'blue',[30]);d.tag('C12',2850,1181)
    d.block('address-control',1830,1250,230,100,['地址 / 事务','AR / AW 映射'],'purple',[30,26])
    d.block('metadata',1830,1380,230,65,['块地址 / 元数据'],'purple',[28])
    d.rect('shared-payload-services',2095,1250,815,195,'white',True)
    for id,x,title,desc,tag,fill in [
        ('compressor',2120,'共享压缩器','W 写数据','C15','orange'),
        ('decompressor',2387.5,'共享解压器','R 读数据','C16','orange'),
        ('plain-bypass',2655,'普通数据旁路','W / R 原样',None,'blue')]:
        d.rect(id,x,1290,235,115,fill)
        if tag:d.tag(tag,x+8,1294)
        d.text(id+'-title',x+117.5,1353,title,30,True,owner=id)
        d.text(id+'-detail',x+117.5,1385,desc,26,owner=id)
    d.block('front-route',1830,1475,1080,50,['下游 AXI 路由 / R、B 响应匹配'],'blue',[30])
    d.edge('adapt-address','front-adapt','address-control',[(1945,1220),(1945,1250)])
    d.edge('address-downstream','address-control','front-route',[(2060,1300),(2072,1300),(2072,1475)])
    d.edge('b-response','front-route','front-adapt',[(1830,1500),(1820,1500),(1820,1240),(1845,1240),(1845,1220)])
    d.text('b-response-label',1865,1246,'B',24,color='data')
    d.edge('metadata-control','address-control','metadata',[(1945,1350),(1945,1380)],'cfg',both=True)
    d.edge('metadata-storage','metadata','front-route',[(1945,1445),(1945,1475)],both=True)
    for id,x in [('compressor',2237.5),('decompressor',2505),('plain-bypass',2772.5)]:
        if id=='decompressor':
            d.edge('read-to-decoder','front-route',id,[(x,1475),(x,1405)])
            d.edge('decoder-up',id,'front-adapt',[(x,1290),(x,1220)])
        else:
            d.edge('adapt-'+id,'front-adapt',id,[(x,1220),(x,1290)],both=id=='plain-bypass')
            d.edge(id+'-route',id,'front-route',[(x,1405),(x,1475)],both=id=='plain-bypass')
    for i,x in enumerate(ports):
        b=box(f'ddr-S{i}');b['x']=x-75;b['w']=150
        text(f'ddr-S{i}-t0')['text']=f'DDR.S{i}'
        d.edge(f'front-ddr-{i}','front-route',f'ddr-S{i}',[(x,1525),(x,1551)])
    for name in ['llc-f0','mover-f1','frame-f2']:
        e=edge(name);e['points'][-1]=(e['points'][-1][0],1116);e['dash']=False
    edge('roi-f3-request')['points']=[(3030,1345),(2975,1345),(2975,1105),(2775,1105),(2775,1116)]
    remove_edges({'f3-roi-read-data'})

    # Keep the vertical output placement, reserve space for individual config badges.
    remove_objects({'roi-scheduler','roi-vdma','roi-fifo','lvds-tx','badge-C11'})
    for id,y,h,title,desc,tag in [
        ('roi-scheduler',1210,100,'ROI 任务表','顺序调度','C11'),
        ('roi-vdma',1325,100,'帧输出 VDMA','二维 AXI 读','C13'),
        ('roi-fifo',1440,75,'像素整理','输出 FIFO',None),
        ('lvds-tx',1530,100,'LVDS TX','子图帧行封装','C14')]:
        if tag:
            d.rect(id,3030,y,260,h,'white');d.tag(tag,3230,y+4)
            d.text(id+'-title',3160,y+62,title,30,True,owner=id)
            d.text(id+'-detail',3160,y+92,desc,26,owner=id)
        else:d.block(id,3030,y,260,h,[title,desc],'white',[30,26])
    edge('roi-vdma-control')['points']=[(3160,1310),(3160,1325)]
    edge('vdma-pixels')['points']=[(3160,1425),(3160,1440)]
    edge('fifo-lvds')['points']=[(3160,1515),(3160,1530)]

    # Colour represents interface semantics; dashes are reserved for optional/planned boxes.
    edge('isp-gb')['dash']=False
    edge('master-8')['kind']='data'
    edge('emmc-physical')['kind']='optional'
    remove_edges({e['id'] for e in d.edges if e['id'].startswith('legend-')})
    d.texts[:]=[t for t in d.texts if not t['id'].startswith('legend-')]
    for i,(kind,txt) in enumerate([('data','AXI 请求方向'),('gb','GB 局部读写'),('pixel','像素流'),('cfg','配置 / 控制'),('optional','eMMC 接口')]):
        y=720+i*67
        d.edge('legend-'+kind,'legend','legend',[(3010,y),(3060,y)],kind,both=kind in ['gb','optional'])
        d.text('legend-'+kind+'-text',3180,y+10,txt,26,color=kind)
    d.text('legend-return',3160,1052,'AXI 响应：沿原接口返回',24,color='data')
    d.text('legend-status',3160,1085,'虚线框：规划 / 可选',24,color='muted')
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--native-skill-root',type=Path,required=True);a=p.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=False)
    fills,theme=source_colours(a.input);d=revised(fills,theme);svg=a.out_dir/'slide-04.svg';d.save(svg)
    subprocess.run(['python3','-B',str(a.native_skill_root/'scripts/run.py'),'--input',str(svg),'--out-dir',str(a.out_dir/'native'),'--aspect','source','--slide-width-in',str(12192000/914400),'--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    revise(a.input,a.out_dir/'native/diagrams.pptx',a.out_dir/'soc_landscape_m5_gb.pptx',fills)
    (a.out_dir/'colour_map.json').write_text(json.dumps({k:{'source_name':v,'rgb':resolve_colour(fills[v],theme)} for k,v in MATCH.items()},ensure_ascii=False,indent=2)+'\n')
    (a.out_dir/'config_bindings.json').write_text(json.dumps({f'C{i}':{'module':module,'label':lines} for i,(module,lines) in enumerate(CONFIG,1)},ensure_ascii=False,indent=2)+'\n')
    print('Generated page 4 with 16 configuration groups and shared channel services.')

if __name__=='__main__':main()
