const route=document.querySelector('.bts-timeline');
const entries=[...document.querySelectorAll('.timeline-entry')];
const links=[...document.querySelectorAll('[data-timeline-year]')];
const years=document.querySelector('.timeline-year-links');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let pending=false,active=-1;
function update(){
 pending=false;if(!route||!entries.length)return;
 const r=route.getBoundingClientRect(),focus=innerHeight*.43;
 route.style.setProperty('--route-progress',String(Math.max(0,Math.min(1,(focus-r.top)/Math.max(1,r.height-80)))));
 let next=0;entries.forEach((entry,i)=>{if(entry.getBoundingClientRect().top<=focus)next=i});
 if(next===active)return;active=next;
 entries.forEach((entry,i)=>{entry.classList.toggle('is-current',i===active);entry.classList.toggle('is-past',i<active)});
 links.forEach((link,i)=>{if(i===active)link.setAttribute('aria-current','step');else link.removeAttribute('aria-current')});
 const link=links[active];if(years&&link)years.scrollTo({left:link.offsetLeft-years.offsetLeft-years.clientWidth/2+link.clientWidth/2,behavior:reduced.matches?'instant':'smooth'});
}
function requestUpdate(){if(!pending){pending=true;requestAnimationFrame(update)}}
addEventListener('scroll',requestUpdate,{passive:true});addEventListener('resize',requestUpdate,{passive:true});
if(route)new ResizeObserver(requestUpdate).observe(route);document.fonts.ready.then(requestUpdate);requestUpdate();
document.querySelectorAll('.chapter-picker nav a').forEach(a=>a.addEventListener('click',()=>{a.closest('details').open=false}));
