import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const root=new URL('../dist/',import.meta.url);
for(const lang of ['th','en']){
 test(`${lang}: business cards and sustainability button open their existing pages`,()=>{
  const html=readFileSync(new URL(`${lang}/home/index.html`,root),'utf8');
  assert.doesNotMatch(html,/class="home-shortcuts"/);
  for(const slug of ['move','mix','match']){
   const tag=[...html.matchAll(/<a\b[^>]*>/g)].map(m=>m[0]).find(t=>t.includes(`data-business="${slug}"`));
   assert.ok(tag,`Missing business card ${slug}`);
   assert.ok(tag.includes(`href="/${lang}/our-business/${slug}/"`));
   assert.ok(existsSync(new URL(`${lang}/our-business/${slug}/index.html`,root)));
  }
  const scene=html.match(/<section\b[^>]*id="sustainability"[^>]*>[\s\S]*?<\/section>/)?.[0];
  assert.ok(scene,'Missing sustainability scene');
  const links=[...scene.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>/g)];
  const destination=`${lang}/sustainability/sustainability-at-bts-group/`;
  assert.deepEqual(links.map(link=>link[1]), [`/${destination}`]);
  assert.ok(existsSync(new URL(`${destination}index.html`,root)));
 });
}
