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

def footer(lang, nodes):
    th = lang == 'th'
    nodes = [n for n in nodes if n['key'] != 'home']
    def links(items):
        return ''.join(f'<a href="{escape(first(n))}">{escape(n["label"])}<span aria-hidden="true">↗</span></a>' for n in items)
    company = 'บริษัท บีทีเอส กรุ๊ป โฮลดิ้งส์<br>จำกัด (มหาชน)' if th else 'BTS Group Holdings<br>Public Company Limited'
    address = '1000/9 อาคาร บีทีเอส วิชันนารี ปาร์ค – เซาธ์ ทาวเวอร์ ชั้นที่ 33<br>ถนนพหลโยธิน แขวงจอมพล เขตจตุจักร กรุงเทพฯ 10900' if th else '1000/9 BTS Visionary Park – South Tower, 33rd Floor<br>Phahonyothin Road, Chom Phon, Chatuchak, Bangkok 10900'
    return f'''<footer class="bts-footer footer-modern footer-bts" id="site-footer">
      <div class="footer-signature"><span class="footer-eyebrow">BTS GROUP</span><p>Borderless <span>Transform</span> Solutions</p><a href="/{lang}/contact/">{'เชื่อมต่อกับเรา' if th else 'Connect with us'}<span aria-hidden="true">↗</span></a></div>
      <div class="footer-main-grid">
        <div class="footer-identity"><a class="footer-logo" href="/{lang}/home/" aria-label="BTS Group"><img src="/assets/bts-logo.svg" alt="BTS Group" width="50" height="70"></a><h3>{company}</h3><span class="footer-identity-rule" aria-hidden="true"></span></div>
        <nav class="footer-navigation" aria-label="{'เมนูท้ายเว็บไซต์' if th else 'Footer navigation'}"><h3>{'สำรวจบีทีเอสกรุ๊ป' if th else 'Explore BTS Group'}</h3><div class="footer-link-columns"><div>{links(nodes[:4])}</div><div>{links(nodes[4:])}</div></div></nav>
        <div class="footer-connect"><h3>{'ติดต่อบีทีเอสกรุ๊ป' if th else 'Contact BTS Group'}</h3><p>{address}</p><a class="footer-phone" href="tel:+6620801000"><span>{'โทรศัพท์' if th else 'Telephone'}</span>+66 (0) 2 080 1000<span aria-hidden="true">↗</span></a><a class="footer-location" href="/{lang}/contact/">{'ข้อมูลติดต่อและแผนที่' if th else 'Contact details & location'}<span aria-hidden="true">↗</span></a></div>
      </div>
      <div class="footer-legal"><span>© 2026 BTS Group Holdings Public Company Limited</span><nav aria-label="{'ข้อมูลเว็บไซต์' if th else 'Website information'}"><a href="/{lang}/privacy-statement/">{'นโยบายความเป็นส่วนตัว' if th else 'Privacy Statement'}</a><a href="/{lang}/cookies-policy/">{'นโยบายคุกกี้' if th else 'Cookies Policy'}</a><a href="/{lang}/sitemap/">{'แผนผังเว็บไซต์' if th else 'Sitemap'}</a></nav><button class="back-top" aria-label="{'กลับด้านบน' if th else 'Back to top'}"><span aria-hidden="true">↑</span></button></div>
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
        old.replace_with(BeautifulSoup(footer(lang, catalog['navigation'][lang]), 'html.parser'))
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
