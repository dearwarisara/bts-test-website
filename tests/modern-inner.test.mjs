import test from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync,readFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dist=fileURLToPath(new URL('../dist/',import.meta.url));
function files(dir){return readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):e.name.endsWith('.html')?[path.join(dir,e.name)]:[])}
test('every other internal page ships the modern theme and retains BTS font assets',()=>{
 let count=0;
 for(const f of files(dist)){
  const html=readFileSync(f,'utf8'),body=html.match(/<body\b[^>]*class="([^"]*)"/)?.[1]||'';
  if(!body.split(' ').includes('inner-page')||body.split(' ').includes('ir-home-page'))continue;
  count++;
  assert.ok(body.split(' ').includes('modern-inner'),f);
  for(const asset of ['/bts-modern-inner.css?v=1','/bts-modern-inner.js?v=1','/bts-brand.css'])assert.ok(html.includes(asset),`${f}: ${asset}`);
 }
 const report=JSON.parse(readFileSync(new URL('../modern-inner-report.json',import.meta.url),'utf8'));
 assert.equal(count,report.pages);
 for(const asset of ['bts-modern-inner.css','bts-modern-inner.js','assets/DBOzoneXRegular.woff','assets/Mulish-Regular.woff2'])assert.ok(existsSync(path.join(dist,asset)),asset);
});
