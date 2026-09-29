'use strict';
// Progressive enhancement: all substantive content and figures exist in HTML/SVG.
document.querySelectorAll('[data-stepper]').forEach(box => {
  const steps = [...box.querySelectorAll('.steps li')];
  const text = box.querySelector('.step-text');
  const notes = [...box.querySelectorAll('details p')].map(p => p.textContent);
  let index = 0;
  function show() { steps.forEach((s,i) => {s.classList.toggle('active', i===index); s.setAttribute('aria-current', i===index ? 'step':'false');}); text.textContent = `${index+1}/${steps.length} · ${notes[index]}`; }
  box.querySelector('button').addEventListener('click', () => { index=(index+1)%steps.length; show(); });
  show();
});
const calc=document.querySelector('#ai-calc');
if(calc){
  function update(){
    const v=Object.fromEntries([...calc.querySelectorAll('input')].map(x=>[x.name,Number(x.value)]));
    const out=document.querySelector('#calc-result');
    if(Object.values(v).some(n=>!Number.isFinite(n)||n<=0)){out.textContent='请输入大于 0 的有限数值。';return;}
    const weights=v.params*1e9*v.bits/8;
    const kv=2*v.layers*v.heads*v.dim*v.context*v.batch*v.kvbytes;
    const total=(weights+kv+v.activation*2**20)*(1+v.reserve/100);
    const traffic=weights+kv/v.batch;
    out.textContent=`权重 ${(weights/2**30).toFixed(2)} GiB；KV ${(kv/2**30).toFixed(2)} GiB；含激活及余量 ${ (total/2**30).toFixed(2)} GiB。单请求逐 token 无权重复用时，权重+全 KV 读取约 ${(traffic/1e9).toFixed(2)} GB/token；${v.tps} token/s 约需 ${(traffic*v.tps/1e9).toFixed(2)} GB/s 有效带宽（未含其他流量）。`;
  }
  calc.addEventListener('input',update);update();
}
document.querySelectorAll('table').forEach(t=>{const w=document.createElement('div');w.className='table-wrap';t.before(w);w.append(t);});
document.querySelectorAll('figure').forEach(f=>{
  const img=f.querySelector('img');if(!img)return;
  const bar=document.createElement('div');bar.className='figure-controls';
  const fit=document.createElement('button');fit.type='button';fit.textContent='适应宽度';fit.dataset.figureFit='';
  fit.addEventListener('click',()=>{img.style.minWidth='0';img.style.width='100%';f.scrollLeft=0;});
  const full=document.createElement('button');full.type='button';full.textContent='放大阅读';full.dataset.figureFull='';
  full.addEventListener('click',()=>{img.style.minWidth=img.naturalWidth+'px';});
  const link=document.createElement('a');link.href=img.getAttribute('src');link.textContent='单独打开图';link.target='_blank';link.rel='noopener';
  bar.append(fit,full,link);f.prepend(bar);
});
const regSearch=document.querySelector('#reg-search');
if(regSearch){
  const rows=[...document.querySelectorAll('[data-register]')];
  const count=document.querySelector('#reg-count');
  function filterRegisters(){
    const q=regSearch.value.trim().toLowerCase();let shown=0;
    rows.forEach(r=>{const match=(r.dataset.register+' '+r.textContent).toLowerCase().includes(q);r.hidden=!match;if(match)shown++;});
    document.querySelectorAll('.register-group').forEach(g=>{g.hidden=![...g.querySelectorAll('[data-register]')].some(r=>!r.hidden);});
    count.textContent=`显示 ${shown} / ${rows.length} 个寄存器；筛选不进行任何硬件访问。`;
  }
  regSearch.addEventListener('input',filterRegisters);filterRegisters();
}
const selected=document.querySelector('.sidebar nav [aria-current="page"]');
if(selected && matchMedia('(min-width:901px)').matches){
  const sidebar=document.querySelector('.sidebar');
  sidebar.scrollTop=Math.max(0,selected.offsetTop-sidebar.clientHeight/2);
} else if(selected){
  const nav=document.querySelector('.sidebar nav');
  nav.scrollTop+=selected.getBoundingClientRect().top-nav.getBoundingClientRect().top-nav.clientHeight/2;
}
