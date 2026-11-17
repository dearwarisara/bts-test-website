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
 test(`${lang}: level-3 disclosure preserves every header destination and marks its current branch`,()=>{
  const html=readFileSync(path.join(root,`dist/${lang}/investor-relations/document/financial-statements/index.html`),'utf8');
  const header=html.slice(html.indexOf('<header'),html.indexOf('</header>'));
  assert.match(header,/data-navigation-version="3"/);
  assert.match(header,/<details class="nav-branch" open="">/);
  assert.match(header,/<summary>/);
  for(const node of flatten(output[lang]).filter(n=>n.href)){
   assert.ok(header.includes(`href="${node.href}"`),`Missing header route: ${node.href}`);
  }
  const footer=html.slice(html.indexOf('<footer'),html.indexOf('</footer>'));
  assert.match(footer,/footer-modern/);
  assert.match(footer,/tel:\+6620801000/);
  assert.ok(footer.includes(`/${lang}/contact/`));
  assert.match(html,/\/bts-shell\.css\?v=1/);
 });
}
