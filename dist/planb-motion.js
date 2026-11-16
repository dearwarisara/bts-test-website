const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const hero=document.querySelector('.hero');
if(hero?.querySelector('.hero-sticky')){
 let target=0,current=0,raf=0,last=performance.now();
 const draw=now=>{raf=0;const dt=Math.min(.05,(now-last)/1000);last=now;current=reduced.matches?0:current+(target-current)*(1-Math.exp(-dt*9));if(Math.abs(current-target)<.0001)current=target;hero.style.setProperty('--pb-progress',String(current));hero.dataset.scrollProgress=current.toFixed(3);if(!reduced.matches&&Math.abs(current-target)>.0001)raf=requestAnimationFrame(draw)};
 const measure=()=>{const r=hero.getBoundingClientRect();target=reduced.matches?0:Math.max(0,Math.min(1,-r.top/Math.max(1,r.height-innerHeight)));if(!raf){last=performance.now();raf=requestAnimationFrame(draw)}};
 addEventListener('scroll',measure,{passive:true});addEventListener('resize',measure,{passive:true});reduced.addEventListener('change',()=>{if(reduced.matches)hero.querySelector('video')?.pause();measure()});measure();
}
const reportButtons=[...document.querySelectorAll('[data-report-tab]')];
function showReport(index){reportButtons.forEach(button=>{const on=Number(button.dataset.reportTab)===index;button.classList.toggle('active',on);button.setAttribute('aria-pressed',String(on))});document.querySelectorAll('[data-report-card]').forEach(card=>card.hidden=Number(card.dataset.reportCard)!==index)}
reportButtons.forEach(button=>button.addEventListener('click',()=>showReport(Number(button.dataset.reportTab))));if(reportButtons.length)showReport(0);
