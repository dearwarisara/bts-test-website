"""Refresh only the shared footer and expandable navigation; preserve page content."""
from pathlib import Path
from html import escape
import json
from bs4 import BeautifulSoup

R = Path(__file__).parent
D = R / 'dist'

def first(node):
    return node.get('href') or next((first(n) for n in node.get('children', []) if first(n)), '')

def nav_tree(nodes, current, level=2):
    items = []
    for n in nodes:
        label = escape(n['label'])
        href = n.get('href')
        children = n.get('children', [])
        active = href and href.rstrip('/') == current.rstrip('/')
        if children:
            contains = any(current.rstrip('/') == p.rstrip('/') for p in all_hrefs(children))
            overview = f'<li><a href="{escape(href)}">{label}<span aria-hidden="true">↗</span></a></li>' if href else ''
            subtree = nav_tree(children, current, level + 1)
            if overview: subtree = subtree.replace('>', '>' + overview, 1)
            item = f'<details class="nav-branch"'+(' open' if contains else '')+f'><summary><span>{label}</span><span class="nav-chevron" aria-hidden="true"></span></summary>{subtree}</details>'
        else:
            item = f'<a href="{escape(href or "#")}"'+(' aria-current="page"' if active else '')+f'><span>{label}</span><span class="nav-link-arrow" aria-hidden="true">↗</span></a>'
        items.append('<li>' + item + '</li>')
    if level == 2:
        split = (len(items) + 1) // 2
        return '<div class="nav-index-columns"><ul class="nav-level-2">' + ''.join(items[:split]) + '</ul><ul class="nav-level-2">' + ''.join(items[split:]) + '</ul></div>'
    return f'<ul class="nav-level-{level}">' + ''.join(items) + '</ul>'

def all_hrefs(nodes):
    return [h for n in nodes for h in ([n['href']] if n.get('href') else []) + all_hrefs(n.get('children', []))]

def footer(lang):
    labels = {
        'th': {
            'ir': 'ฝ่ายนักลงทุนสัมพันธ์',
            'company': 'บริษัท บีทีเอส กรุ๊ป โฮลดิ้งส์ จำกัด (มหาชน)',
            'address': '1000/9 อาคาร บีทีเอส วิชันนารี ปาร์ค – นอร์ท ทาวเวอร์ ชั้นที่ 34<br>ถนนพหลโยธิน แขวงจอมพล เขตจตุจักร กรุงเทพฯ 10900',
            'phone': 'โทรศัพท์',
            'extension': 'ต่อ 6005 หรือ 6007',
            'email': 'อีเมล',
            'contact': 'ติดต่อนักลงทุนสัมพันธ์',
            'links': 'เว็บไซต์ที่เกี่ยวข้อง',
            'updates': 'ติดตามข่าวสาร BTS Group',
            'legal': 'ข้อมูลเว็บไซต์',
            'top': 'กลับด้านบน',
        },
        'en': {
            'ir': 'Investor Relations',
            'company': 'BTS Group Holdings Public Company Limited',
            'address': '1000/9 BTS Visionary Park – North Tower, 34th Floor<br>Phahonyothin Road, Chom Phon, Chatuchak, Bangkok 10900',
            'phone': 'Telephone',
            'extension': 'ext. 6005 or 6007',
            'email': 'Email',
            'contact': 'Contact Investor Relations',
            'links': 'Related Websites',
            'updates': 'BTS Group Updates',
            'legal': 'Website information',
            'top': 'Back to top',
        },
    }[lang]

    def links(items, arrows=False):
        icon = ' <span aria-hidden="true">↗</span>' if arrows else ''
        return ''.join(
            f'<a href="/{lang}/{path}/">{th if lang == "th" else en}{icon}</a>'
            for path, th, en in items
        )

    related = links([
        ('our-business/business-overview', 'ธุรกิจของเรา', 'Our Business'),
        ('investor-relations/home', 'นักลงทุนสัมพันธ์', 'Investor Relations'),
        ('sustainability/sustainability-at-bts-group', 'ความยั่งยืน', 'Sustainability'),
        ('contact', 'ติดต่อบีทีเอสกรุ๊ป', 'Contact BTS Group'),
    ], arrows=True)
    updates = links([
        ('update/news-event', 'ข่าวสารองค์กร', 'Corporate News'),
        ('corporate-communications/corporate-vdo', 'วิดีโอองค์กร', 'Corporate Videos'),
    ], arrows=True)
    legal = links([
        ('terms-and-conditions', 'ข้อกำหนดและเงื่อนไข', 'Terms and Conditions'),
        ('privacy-statement', 'นโยบายความเป็นส่วนตัว', 'Privacy Statement'),
        ('cookies-policy', 'นโยบายคุกกี้', 'Cookies Policy'),
        ('sitemap', 'แผนผังเว็บไซต์', 'Sitemap'),
    ])

    return f'''<footer class="bts-footer footer-modern footer-reference">
      <div class="footer-reference-grid">
        <div><a class="footer-reference-logo" href="/{lang}/home/"><img src="/assets/bts-logo.svg" alt="BTS Group" width="51" height="69"></a></div>
        <section class="footer-reference-contact" aria-labelledby="footer-ir-title">
          <h2 id="footer-ir-title">{labels['ir']}</h2>
          <p>{labels['company']}<br>{labels['address']}</p>
          <dl>
            <div><dt>{labels['phone']}</dt><dd><a href="tel:+6620801000">+66 (0) 2 080 1000</a> {labels['extension']}</dd></div>
            <div><dt>{labels['email']}</dt><dd><a href="mailto:ir@btsgroup.co.th">ir@btsgroup.co.th</a></dd></div>
          </dl>
          <a class="footer-reference-action" href="/{lang}/investor-relations/information-inquiry/ir-contact/" data-bts-cta>{labels['contact']}<span class="bts-cta-icon" aria-hidden="true">›</span></a>
        </section>
        <div class="footer-reference-links">
          <nav aria-labelledby="footer-related-title"><h2 id="footer-related-title">{labels['links']}</h2><div>{related}</div></nav>
          <nav aria-labelledby="footer-updates-title"><h2 id="footer-updates-title">{labels['updates']}</h2><div>{updates}</div></nav>
        </div>
      </div>
      <div class="footer-reference-legal">
        <p>© 2026 {labels['company']}</p>
        <nav aria-label="{labels['legal']}">{legal}</nav>
        <button type="button" class="back-top" aria-label="{labels['top']}"><span aria-hidden="true"></span></button>
      </div>
    </footer>'''


def main():
    catalog = json.loads((D/'site-catalog.json').read_text(encoding='utf-8'))
    count = 0
    for file in D.rglob('*.html'):
        s = BeautifulSoup(file.read_text(encoding='utf-8-sig'), 'html.parser')
        if not s.select_one('body>footer.bts-footer'): continue
        lang = 'en' if s.html.get('lang') == 'en' else 'th'
        current = '/' + file.parent.relative_to(D).as_posix() + '/'
        old = s.select_one('body>footer.bts-footer')
        old.replace_with(BeautifulSoup(footer(lang), 'html.parser'))
        for group in catalog['navigation'][lang]:
            target = s.select_one(f'#mega-{group["key"]} .official-tree')
            if target:
                target.clear()
                target.append(BeautifulSoup(nav_tree(group.get('children', []), current), 'html.parser'))
        s.select_one('.site-header')['data-navigation-version'] = '3'
        for css in s.select('link[href^="/bts-shell.css"]'): css.decompose()
        s.head.append(s.new_tag('link', rel='stylesheet', href='/bts-shell.css?v=1'))
        file.write_text(str(s), encoding='utf-8')
        count += 1
    print(f'Refreshed {count} footers and level-3 menus.')

if __name__ == '__main__': main()
