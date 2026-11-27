import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const root=new URL('../dist/',import.meta.url);
for(const lang of ['th','en']){
 test(`${lang}: integrated investor scene keeps figures, imagery and working local links`,()=>{
  const html=readFileSync(new URL(`${lang}/home/index.html`,root),'utf8');
  const scene=html.match(/<section\b[^>]*class="investor-overview"[^>]*>[\s\S]*?<\/section>/)?.[0];
  assert.ok(scene,'Missing integrated investor scene');
  assert.doesNotMatch(html,/class="finance-glass"|class="investor-night"/);
  assert.ok(scene.includes('id="publications"'));
  assert.match(scene,/<a\b[^>]*class="investor-overview-primary"[\s\S]*?<\/a>\s*<span class="investor-overview-period">/);
  assert.doesNotMatch(scene,/investor-overview-primary-label/);
  for(const value of ['7,492','2,822','(388)']) assert.ok(scene.includes(value));
  for(const asset of ['ir/connected-city-v1.webp','financial-architecture-panel.png']){
   assert.ok(scene.includes(`/assets/${asset}`));
   assert.ok(existsSync(new URL(`assets/${asset}`,root)));
  }
  for(const [,href] of scene.matchAll(/<a\b[^>]*href="([^"]+)"/g)){
   assert.ok(href.startsWith(`/${lang}/investor-relations/`),`Unexpected investor link: ${href}`);
   assert.ok(existsSync(new URL(`${href.slice(1)}index.html`,root)),`Missing page for ${href}`);
  }
 });
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
