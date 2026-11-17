import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
test('IR concept illustration is available to the deployed pages',()=>{
 assert.ok(existsSync(new URL('../dist/assets/ir/connected-city-v1.webp',import.meta.url)));
});
for(const path of ['index.html','th/home/index.html','en/home/index.html']){
 test(`${path}: homepage uses the original BTS tiger film`,()=>{
  const html=readFileSync(new URL('../dist/'+path,import.meta.url),'utf8');
  const hero=html.match(/<video\b[^>]*id="hero-video"[\s\S]*?<\/video>/)?.[0];
  assert.ok(hero);
  assert.ok(hero.includes('https://www.btsgroup.co.th/storage/bilboard/video-banner.mp4'));
  assert.ok(!hero.includes('storage/investor-relations/'));
 });
}
for(const lang of ['th','en']){
 test(`${lang}: rail video is in the IR cover without a duplicate body player`,()=>{
  const html=readFileSync(new URL(`../dist/${lang}/investor-relations/home/index.html`,import.meta.url),'utf8');
  assert.equal((html.match(/<video\b/g)||[]).length,1);
  const video=html.match(/<video\b[^>]*class="cover-video"[\s\S]*?<\/video>/)?.[0];
  assert.ok(video?.includes('storage/investor-relations/home/video-banner.mp4'));
  for(const attr of ['autoplay','muted','playsinline','loop'])assert.ok(video.includes(attr));
  assert.doesNotMatch(video,/\bcontrols\b/);
  assert.doesNotMatch(html,/class="ir-banner"/);
  assert.match(html,/class="cover-video-toggle"/);
  assert.match(html,/data-ir-documents/);
  assert.ok(html.includes('/ir-home.css?v=3'));
  assert.doesNotMatch(html,/class="modal fade/);
  assert.ok(html.includes('/cover-video.js?v=1'));
 });
}
