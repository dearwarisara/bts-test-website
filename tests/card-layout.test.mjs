import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
const root=new URL('../dist/',import.meta.url);
function files(dir){return readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(new URL(e.name+'/',dir)):e.name.endsWith('.html')?[new URL(e.name,dir)]:[])}
test('every generated card has a separate padded content box',()=>{
 let count=0;
 for(const file of files(root)){
  const html=readFileSync(file,'utf8');
  for(const m of html.matchAll(/<a\b[^>]*class="page-card"[^>]*>([\s\S]*?)<\/a>/g)){
   count++;assert.match(m[1],/class="page-card-body"/,file.pathname);
  }
 }
 assert.ok(count>0,'Expected generated cards in the remaining page content');
});
test('dynamic cards keep complete sentences and wrap text in the same content box',()=>{
 const src=readFileSync(new URL('content.js',root),'utf8');
 const code=src.slice(src.indexOf('function resultCards('),src.indexOf('async function query('));
 const render=Function('esc',code+';return resultCards;')(s=>String(s??''));
 const sentence='This is a complete sentence describing a business clearly and accurately.';
 const html=render([{path:'/en/our-business/move',href:'/en/our-business/move/',title:'MOVE',group:'our-business',description:sentence+' Additional information. '.repeat(20),image:''}]);
 assert.ok(html.includes(`<p>${sentence}</p>`));
 assert.match(html,/class="page-card-body"/);
 const excerpt=render([{path:'/en/other',href:'/en/other/',title:'Other',group:'about',description:'Long description without punctuation '.repeat(20),image:''}]);
 assert.match(excerpt,/<p>[^<]+…<\/p>/);
});
