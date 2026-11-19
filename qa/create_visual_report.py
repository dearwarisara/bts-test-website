"""Package the final full-page desktop and mobile review evidence."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / '.visual-qa-inner'
routes = json.loads((QA / 'routes.json').read_text(encoding='utf-8'))
latest = {}
for line in (QA / 'checks.jsonl').read_text(encoding='utf-8').splitlines():
    item = json.loads(line)
    latest[(item['viewport'], item['index'])] = item

viewports = {}
for name in ('desktop', 'mobile'):
    items = [latest[(name, i)] for i in range(len(routes))]
    viewports[name] = {
        'pages': len(items),
        'widths': sorted({item['width'] for item in items}),
        'checks': {
            'horizontal_overflow': sum(bool(item['overflow']) for item in items),
            'broken_images': sum(len(item['broken']) for item in items),
            'clipped_text_elements': sum(len(item['clipped']) for item in items),
        },
        'screenshots': f'.visual-qa-inner/{name}/<route-index>.jpg',
    }
report = {
    'reviewed_at': '2026-11-19',
    'routes': len(routes),
    'viewports': viewports,
    'font_assets': ['OzoneX Thai', 'Mulish English'],
    'references': ['Ichitan Group', 'Metro Systems', 'CH. Karnchang', 'TTW', 'Sabina', 'PTTGC', 'Bangkok Airways'],
    'news_archive_images': {
        'representative_cards': 4,
        'archive_pages': ['TH corporate news', 'EN corporate news', 'TH updates', 'EN updates'],
        'other_cards': 'Text-only cards with the empty image area removed.',
    },
    'notes': 'Screenshots are browser full-page captures at responsive viewport widths; this is not physical-device testing. Interactions were spot-checked for financial-period switching and the nested investor-relations menu.',
}
(ROOT / 'inner-visual-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

cards = []
for index, route in enumerate(routes):
    safe = route.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    cards.append(
        f'<article data-route="{safe.lower()}"><a href="http://127.0.0.1:4173{safe}">{safe}</a>'
        f'<div class="pair"><a href="desktop/{index}.jpg"><img loading="lazy" src="desktop/{index}.jpg" alt="Desktop screenshot {index}"></a>'
        f'<a href="mobile/{index}.jpg"><img loading="lazy" src="mobile/{index}.jpg" alt="Mobile screenshot {index}"></a></div></article>'
    )
html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>BTS inner pages visual review</title>
<style>body{margin:0;background:#f2f6fa;color:#12365a;font:15px/1.5 Arial,sans-serif}header{position:sticky;top:0;background:#fff;padding:18px 4vw;box-shadow:0 2px 12px #1232;z-index:2}h1{margin:0 0 8px;font-size:22px}input{width:min(440px,90vw);padding:10px;border:1px solid #c8d7e6;border-radius:6px}main{padding:24px 4vw;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px}article{background:#fff;border:1px solid #d7e3ee;border-radius:10px;padding:12px;overflow:hidden}article>a{display:block;overflow-wrap:anywhere;margin-bottom:10px;color:#07589a}.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px}.pair img{width:100%;height:390px;object-fit:contain;object-position:top;background:#e8eef4;border:1px solid #dbe4ed;border-radius:5px}small{color:#627b91}</style>
<header><h1>BTS Group · Internal page visual review</h1><small>999 routes · full-page desktop and mobile captures · select a thumbnail to open the full image</small><p><input id="filter" placeholder="Filter routes, e.g. investor-relations"></p></header><main>''' + ''.join(cards) + '''</main><script>document.querySelector('#filter').addEventListener('input',e=>{const q=e.target.value.toLowerCase();for(const c of document.querySelectorAll('article'))c.hidden=!c.dataset.route.includes(q)})</script></html>'''
(QA / 'index.html').write_text(html, encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
