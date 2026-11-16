import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
for(const lang of ['th','en']){
 test(`${lang}: full-width timeline retains all 21 years with native jump links`,()=>{
  const html=readFileSync(new URL(`../dist/${lang}/about/our-history/index.html`,import.meta.url),'utf8');
  const entries=[...html.matchAll(/<li[^>]+class="timeline-entry"[^>]+data-year="([^"]+)"[^>]+id="(year-\d+)"/g)];
  assert.equal(entries.length,21);
  assert.equal(new Set(entries.map(m=>m[2])).size,21);
  for(const match of entries)assert.ok(html.includes(`href="#${match[2]}"`));
  assert.equal((html.match(/class="history-event-copy timeline-copy"/g)||[]).length,21);
  const art=[...html.matchAll(/<figure class="timeline-art">[\s\S]*?<img[^>]+src="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(art.length,21);assert.equal(new Set(art).size,21);
  for(const src of art)assert.ok(existsSync(new URL('../dist'+src,import.meta.url)),src);
  assert.match(html,/class="timeline-train"/);
  assert.ok(html.includes('/assets/bts-timeline-train.svg'));
  assert.doesNotMatch(html,/<canvas|history-world\.js|chapter-motion\.js/);
 });
}
