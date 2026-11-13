import { cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const output = path.resolve(process.env.SITE_OUTPUT_DIR || path.join(root, '.pages-build'));
const base = (process.env.SITE_BASE_PATH ?? '/bts-test-website').replace(/\/$/, '');
if (!/^(\/[a-zA-Z0-9_.-]+)*$/.test(base)) throw new Error('Invalid Pages base path');
await mkdir(output, { recursive: true });
await cp(path.join(root, 'dist'), output, { recursive: true });
let htmlCount = 0;
async function prepare(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) { await prepare(file); continue; }
    if (entry.name.endsWith('.html')) {
      let html = await readFile(file, 'utf8');
      html = html.replace(/\b(href|src|poster|action)=(['"])(\/(?!\/)[^'"<>]*)\2/g,
        (_, attr, quote, url) => `${attr}=${quote}${url.startsWith('/storage/') ? 'https://www.btsgroup.co.th' : base}${url}${quote}`);
      await writeFile(file, html);
      htmlCount++;
    } else if (entry.name.endsWith('.css')) {
      const css = await readFile(file, 'utf8');
      await writeFile(file, css.replace(/url\((['"]?)(\/(?!\/)[^'"\)]+)\1\)/g,
        (_, quote, url) => `url(${quote}${base}${url}${quote})`));
    }
  }
}
await prepare(output);
const catalogueFile = path.join(output, 'site-catalog.json');
const catalogue = JSON.parse(await readFile(catalogueFile, 'utf8'));
for (const page of catalogue.pages) if (page.href?.startsWith('/')) page.href = base + page.href;
function rebaseNavigation(nodes){for(const node of nodes){if(node.href?.startsWith('/'))node.href=base+node.href;if(node.children)rebaseNavigation(node.children);}}
for(const nodes of Object.values(catalogue.navigation||{}))rebaseNavigation(nodes);
await writeFile(catalogueFile, JSON.stringify(catalogue));
const navFile = path.join(output, 'navigation.js');
let nav = await readFile(navFile, 'utf8');
nav = nav.replace("fetch('/site-catalog.json", `fetch('${base}/site-catalog.json`)
  .replace('||`/${lang===', '||`'+base+'/${lang===');
await writeFile(navFile, nav);
const detailFile = path.join(output, 'details.js');
await writeFile(detailFile, (await readFile(detailFile, 'utf8'))
  .replace("'/assets/bts-logo.svg'", `'${base}/assets/bts-logo.svg'`));
await writeFile(path.join(output, '.nojekyll'), '');
console.log(`Prepared ${htmlCount} pages for ${base || '/'}`);
