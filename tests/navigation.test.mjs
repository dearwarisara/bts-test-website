import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync,existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root=fileURLToPath(new URL('../',import.meta.url));
const source=JSON.parse(readFileSync(path.join(root,'navigation-tree.json'),'utf8')).navigation;
const output=JSON.parse(readFileSync(path.join(root,'dist/site-catalog.json'),'utf8')).navigation;
const semantic=nodes=>nodes.map(n=>({label:n.label,path:n.path,children:semantic(n.children||[])}));
const flatten=nodes=>nodes.flatMap(n=>[n,...flatten(n.children||[])]);

for(const lang of ['th','en']){
 test(`${lang}: menu keeps the official sitemap labels, order and nesting`,()=>{
  assert.deepEqual(semantic(output[lang]),semantic(source[lang]));
  assert.equal(output[lang].length,9);
  const ir=output[lang].find(n=>n.key==='investor-relations');
  assert.ok(ir.children.some(n=>n.children?.length===6),'financial subpages must remain grouped');
 });
 test(`${lang}: every menu link has its own working route and appears on the sitemap`,()=>{
  const links=flatten(output[lang]).filter(n=>n.href);
  for(const node of links){assert.ok(node.href.startsWith(`/${lang}/`));assert.ok(existsSync(path.join(root,'dist',node.href.slice(1),'index.html')),node.href);}
  const html=readFileSync(path.join(root,`dist/${lang}/sitemap/index.html`),'utf8');
  const match=/<nav\b[^>]*\bclass="sitemap-tree"[^>]*>/.exec(html);
  const start=match?.index??-1,end=html.indexOf('</nav>',start);
  assert.ok(start>=0&&end>start);
  assert.equal((html.slice(start,end).match(/<a\s/g)||[]).length,links.length);
 });
}
