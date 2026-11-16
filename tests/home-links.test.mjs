import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const root=new URL('../dist/',import.meta.url);
for(const lang of ['th','en']){
 test(`${lang}: business cards and sustainability rows open their own existing pages`,()=>{
  const html=readFileSync(new URL(`${lang}/home/index.html`,root),'utf8');
  assert.doesNotMatch(html,/class="home-shortcuts"/);
  for(const slug of ['move','mix','match']){
   const tag=[...html.matchAll(/<a\b[^>]*>/g)].map(m=>m[0]).find(t=>t.includes(`data-business="${slug}"`));
   assert.ok(tag,`Missing business card ${slug}`);
   assert.ok(tag.includes(`href="/${lang}/our-business/${slug}/"`));
   assert.ok(existsSync(new URL(`${lang}/our-business/${slug}/index.html`,root)));
  }
  const destinations=['sustainability/environmental-sustainability','sustainability/social-sustainability','corporate-governance/at-a-glance'];
  for(const [i,path] of destinations.entries()){
   const tag=[...html.matchAll(/<a\b[^>]*>/g)].map(m=>m[0]).find(t=>t.includes(`data-esg="${i}"`));
   assert.ok(tag,`ESG ${i} must be a navigable link`);
   assert.ok(tag.includes(`href="/${lang}/${path}/"`));
   assert.ok(existsSync(new URL(`${lang}/${path}/index.html`,root)));
  }
 });
}
