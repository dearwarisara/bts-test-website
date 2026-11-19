import fs from 'node:fs/promises';
const root='D:/Optiwise Dropbox/Warisara Khamnuengsitti/Obsidian/bts-group-home-refresh';
const output=root+'/.visual-qa-inner';
const routes=JSON.parse(await fs.readFile(output+'/routes.json','utf8'));
export async function run(tab,start,end,viewport){for(let index=start;index<end;index++){
 await tab.goto('http://127.0.0.1:4173'+routes[index]+'?visual_review=1');
 await tab.playwright.waitForLoadState({state:'load'});
 await tab.playwright.evaluate(async()=>{await document.fonts.ready});
 const check=await tab.playwright.evaluate(()=>({path:location.pathname,width:innerWidth,height:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth&&i.getBoundingClientRect().width>1).map(i=>i.getAttribute('src')),clipped:[...document.querySelectorAll('main h1,main h2,main h3,main p,.card-title,.card-text')].filter(e=>e.clientWidth&&e.scrollWidth>e.clientWidth+4&&!e.closest('.table-responsive,.table-scroll')).map(e=>e.textContent.slice(0,70))}));
 await fs.writeFile(output+'/'+viewport+'/'+index+'.jpg',await tab.screenshot({fullPage:true}));
 await fs.appendFile(output+'/checks.jsonl',JSON.stringify({...check,index,viewport})+'\n');
 }return {viewport,through:end};}
export async function selected(tab,indices,viewport){for(const i of indices)await run(tab,i,i+1,viewport);return {viewport,count:indices.length};}
