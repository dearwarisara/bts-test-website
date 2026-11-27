from pathlib import Path
from calendar import month_name
from datetime import date
from hashlib import sha256
import json
import re

from bs4 import BeautifulSoup
from refresh_shared_shell import footer


BUTTON_LINKS = (
 'a.outline-button, a.official-action, a.btn, a.btn-back, a.finance-glass-action, '
 'a.investor-night-action, a.hero-discover, a.inner-content-link, a.chapter-back, '
 'a.card-link--icon-next, .footer-contact-action, .sustainability-feature-action, button.archive-more'
)
EDGE_ARROWS = re.compile(r'^←\s*|\s*[↗→↓]$')


def style_action_buttons(page):
 for button in page.select(BUTTON_LINKS):
  if button.has_attr('data-bts-cta'):
   continue
  classes = button.get('class', [])
  label = button.get_text(' ', strip=True)
  arrow = '↗'
  if 'btn-pdf' in classes or 'archive-more' in classes or label.endswith('↓'):
   arrow = '↓'
  elif 'btn-back' in classes or 'chapter-back' in classes or label.startswith('←'):
   arrow = '←'

  for icon in button.find_all(['span', 'b'], recursive=False):
   if icon.get_text(strip=True) in ('↗', '→', '↓', '←') and not icon.find():
    icon.decompose()
  text_nodes = [node for node in button.find_all(string=True) if node.strip()]
  if text_nodes:
   for node in dict.fromkeys((text_nodes[0], text_nodes[-1])):
    cleaned = EDGE_ARROWS.sub('', node.strip())
    if cleaned != node.strip():
     node.replace_with(cleaned)

  button['data-bts-cta'] = ''
  if not button.get_text(strip=True):
   button['data-cta-icon-only'] = ''
   if not any(button.get(attr) for attr in ('aria-label', 'aria-labelledby', 'title')):
    is_thai = page.html.get('lang') == 'th'
    button['aria-label'] = ('ดาวน์โหลด' if is_thai else 'Download') if arrow == '↓' else (
     'ดูออนไลน์' if is_thai else 'View online')
  icon = page.new_tag('span', attrs={'class': 'bts-cta-icon', 'aria-hidden': 'true'})
  icon.string = arrow
  button.append(icon)

def apply_finance_scene(page, language):
 section = page.select_one('.financial-home, .finance-glass')
 if section is None:
  return

 is_thai = language == 'th'
 period_node = section.select_one('.financial-period, .finance-glass-period')
 period = period_node.get_text(' ', strip=True)
 period = period.removeprefix('ข้อมูลสำคัญทางการเงินประจำ' if is_thai else 'Financial Highlights ')
 period = period.split('·', 1)[0].strip()
 figures = [figure.extract() for figure in section.select('.metric strong, .finance-glass-card strong')]
 finance_url = section.select_one('.finance-actions a, .finance-glass-action')['href']

 section.clear()
 section['class'] = ['finance-glass']
 section['aria-labelledby'] = 'finance-glass-title'
 scene = BeautifulSoup("""
 <div class="finance-glass-inner">
  <header class="finance-glass-heading">
  <h2 id="finance-glass-title"></h2>
  <p class="finance-glass-period"></p>
  </header>
  <dl class="finance-glass-metrics"></dl>
  <a class="finance-glass-action"><span aria-hidden="true">↗</span></a>
 </div>
 """, 'html.parser').div

 scene.h2.string = 'ข้อมูลสำคัญทางการเงิน' if is_thai else 'Key Financial Data'
 scene.p.string = period

 labels = ('รายได้รวม', 'EBITDA', 'กำไร (ขาดทุน)') if is_thai else (
  'Total Revenue', 'EBITDA', 'Net Profit (Loss)')
 details = 'สุทธิส่วนที่เป็นของผู้ถือหุ้น' if is_thai else 'Attributable to Equity Holders'
 for index, (name, figure) in enumerate(zip(labels, figures)):
  card = page.new_tag('div', attrs={'class': 'finance-glass-card'})
  term = page.new_tag('dt')
  term.string = name
  if index == 2:
   detail = page.new_tag('span', attrs={'class': 'finance-glass-detail'})
   detail.string = details
   term.append(' ')
   term.append(detail)
  value = page.new_tag('dd')
  value.append(figure)
  unit = page.new_tag('span', attrs={'class': 'finance-glass-unit'})
  unit.string = 'ล้านบาท' if is_thai else 'THB million'
  value.append(unit)
  card.extend([term, value])
  scene.dl.append(card)

 scene.a['href'] = finance_url
 scene.a.insert(0, 'ดูข้อมูลทางการเงิน' if is_thai else 'View Financial Data')
 section.append(scene)

def apply_investor_hub(page):
 compact_hub = page.select_one('section.investor-night#publications')
 if compact_hub is not None:
  focus_investor_documents(compact_hub)
  return

 section = page.select_one('section.investor#publications')
 if section is None:
  return

 intro = section.select_one('.investor-intro')
 intro.name = 'header'
 intro['class'] = ['investor-night-intro']
 intro.h2['id'] = 'investor-night-title'
 intro.select_one('.investor-eyebrow')['class'] = ['investor-night-eyebrow']

 resources = section.select_one('.investor-links')
 resources['class'] = ['investor-night-resources']
 for resource in resources.find_all('a', recursive=False):
  resource['class'] = ['investor-night-resource']
  icon = page.new_tag('span', attrs={'class': 'investor-night-icon', 'aria-hidden': 'true'})
  resource.svg.attrs.pop('class', None)
  resource.svg.wrap(icon)
  arrow = resource.b
  arrow.name = 'span'
  arrow['class'] = ['investor-night-arrow']

 action = intro.select_one('.investor-contact').extract()
 action['class'] = ['investor-night-action']
 arrow = action.b
 arrow.name = 'span'
 arrow['class'] = ['investor-night-arrow']
 arrow['aria-hidden'] = 'true'

 section.clear()
 section['class'] = ['investor-night']
 section['aria-labelledby'] = 'investor-night-title'
 inner = page.new_tag('div', attrs={'class': 'investor-night-inner'})
 inner.extend([intro.extract(), resources.extract(), action])
 section.append(inner)
 focus_investor_documents(section)

def focus_investor_documents(section):
 eyebrow = section.select_one('.investor-night-eyebrow')
 if eyebrow is not None:
  eyebrow.decompose()
 for link in section.select('.investor-night-resources a[href]'):
  if link['href'].rstrip('/').endswith('/financial-information/key-financial-data'):
   link.decompose()
 intro_copy = section.select_one('.investor-night-intro > p')
 if intro_copy is not None:
  intro_copy.decompose()

def apply_investor_overview(page, language):
 """Combine the financial figures and investor documents into the approved scene."""
 if page.select_one('section.investor-overview#financial'):
  return
 finance = page.select_one('section.finance-glass#financial')
 hub = page.select_one('section.investor-night#publications')
 if finance is None or hub is None:
  return

 is_thai = language == 'th'
 figures = finance.select('.finance-glass-card strong')
 links = hub.select('.investor-night-resources a[href]')
 if len(figures) != 3 or len(links) != 3:
  return
 finance_href = finance.select_one('.finance-glass-action')['href']
 overview_href = hub.select_one('.investor-night-action')['href']
 document_href = links[0]['href']
 period = finance.select_one('.finance-glass-period').get_text(' ', strip=True)

 scene = BeautifulSoup('''
 <section class="investor-overview" id="financial" aria-labelledby="investor-overview-title">
  <div class="investor-overview-inner">
   <h2 id="investor-overview-title"></h2>
   <div class="investor-overview-grid">
    <div class="investor-overview-finance">
     <div class="investor-overview-finance-head"><h3></h3><span class="investor-overview-period"></span></div>
     <a class="investor-overview-primary" href=""><span class="investor-overview-primary-label"></span><strong></strong><span class="investor-overview-unit"></span></a>
     <div class="investor-overview-secondary"></div>
    </div>
    <a class="investor-overview-city" href="">
     <img src="/assets/ir/connected-city-v1.webp" alt="" loading="lazy" decoding="async"/>
     <span class="investor-overview-photo-copy"><span><strong></strong><small></small></span><span class="investor-overview-arrow" aria-hidden="true">↗</span></span>
    </a>
    <div class="investor-overview-resources" id="publications">
     <a class="investor-overview-architecture" href="">
      <img src="/assets/financial-architecture-panel.png" alt="" loading="lazy" decoding="async"/>
      <span class="investor-overview-architecture-copy"><strong></strong><span class="investor-overview-arrow" aria-hidden="true">↗</span></span>
     </a>
     <div class="investor-overview-documents"><h3></h3><nav aria-label=""></nav></div>
    </div>
   </div>
  </div>
 </section>
 ''', 'html.parser').section

 scene.h2.string = 'นักลงทุนสัมพันธ์' if is_thai else 'Investor Relations'
 scene.select_one('.investor-overview-finance-head h3').string = 'ข้อมูลสำคัญทางการเงิน' if is_thai else 'Key Financial Data'
 scene.select_one('.investor-overview-period').string = period
 primary = scene.select_one('.investor-overview-primary')
 primary['href'] = finance_href
 primary['aria-label'] = ('ดูข้อมูลทางการเงิน' if is_thai else 'View financial data')
 primary.select_one('.investor-overview-primary-label').string = 'รายได้รวม' if is_thai else 'Total Revenue'
 primary.strong.replace_with(figures[0].extract())
 primary.select_one('.investor-overview-unit').string = 'ล้านบาท' if is_thai else 'THB million'

 secondary = scene.select_one('.investor-overview-secondary')
 names = ('EBITDA', 'กำไร (ขาดทุน) สุทธิส่วนของผู้ถือหุ้น') if is_thai else ('EBITDA', 'Net Profit (Loss) Attributable to Equity Holders')
 for label, figure in zip(names, figures[1:]):
  card = page.new_tag('a', href=finance_href, attrs={'class': 'investor-overview-metric'})
  title = page.new_tag('span', attrs={'class': 'investor-overview-metric-label'})
  title.string = label
  value = page.new_tag('span', attrs={'class': 'investor-overview-metric-value'})
  value.append(figure.extract())
  unit = page.new_tag('small')
  unit.string = 'ล้านบาท' if is_thai else 'THB million'
  value.append(unit)
  card.extend([title, value])
  secondary.append(card)

 city = scene.select_one('.investor-overview-city')
 city['href'] = overview_href
 city.select_one('.investor-overview-photo-copy strong').string = 'ภาพรวมนักลงทุน' if is_thai else 'Investor Overview'
 city.select_one('.investor-overview-photo-copy small').string = 'เชื่อมข้อมูลธุรกิจกับอนาคตของเมือง' if is_thai else 'Connecting business with the city’s future'
 architecture = scene.select_one('.investor-overview-architecture')
 architecture['href'] = document_href
 architecture.select_one('strong').string = 'ศูนย์รวมเอกสาร' if is_thai else 'Document Centre'
 documents = scene.select_one('.investor-overview-documents')
 documents.h3.string = 'เข้าถึงข้อมูลสำคัญ' if is_thai else 'Key Resources'
 documents.nav['aria-label'] = documents.h3.string
 for source in links:
  link = page.new_tag('a', href=source['href'])
  label = page.new_tag('span')
  label.string = source.select('span')[1].get_text(' ', strip=True)
  arrow = page.new_tag('span', attrs={'class': 'investor-overview-arrow', 'aria-hidden': 'true'})
  arrow.string = '↗'
  link.extend([label, arrow])
  documents.nav.append(link)

 finance.replace_with(scene)
 hub.decompose()

def apply_news_timeline(page, language, dist):
 section = page.select_one('section#news')
 carousel = section.select_one('.news-carousel') if section else None
 if carousel is None:
  return

 thai_months = ('มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
                'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม')
 months = thai_months if language == 'th' else tuple(month_name)[1:]
 articles = []
 for card in carousel.select('a.news-card'):
  day, month, year = card.time.get_text(' ', strip=True).split()
  full_date = date(int(year) - (543 if language == 'th' else 0), months.index(month) + 1, int(day))
  articles.append((full_date, f'{month} {year}', card))
 if not articles:
  return
 articles.sort(key=lambda article: article[0], reverse=True)

 header = section.select_one('.news-heading').extract()
 header['class'] = ['news-timeline-header']
 header.h2['id'] = 'news-timeline-title'
 section['class'] = ['news-timeline']
 section['aria-labelledby'] = 'news-timeline-title'
 layout = page.new_tag('div', attrs={'class': 'news-timeline-layout'})
 entries = page.new_tag('ol', attrs={'class': 'news-timeline-list'})
 for full_date, month_year, card in articles:
  row = page.new_tag('li')
  link = page.new_tag('a', href=card['href'], attrs={'class': 'news-timeline-entry'})
  published = page.new_tag('time', datetime=full_date.isoformat())
  day_number = page.new_tag('strong')
  day_number.string = str(full_date.day)
  published.extend([day_number, ' ' + month_year])
  icon = page.new_tag('span', attrs={'class': 'news-timeline-arrow', 'aria-hidden': 'true'})
  icon.string = '↗'
  link.extend([published, card.h3.extract(), icon])
  row.append(link)
  entries.append(row)

 latest = articles[0][2]
 preview = page.new_tag('a', href=latest['href'], attrs={
  'class': 'news-timeline-photo',
  'aria-label': entries.h3.get_text(' ', strip=True),
 })
 image_source = latest.img['src']
 local_image = f'assets/covers/{sha256(image_source.encode()).hexdigest()[:16]}-cover.webp'
 image = page.new_tag('img', src='/' + local_image if (dist/local_image).is_file() else image_source,
                      alt='', loading='lazy', decoding='async')
 icon = page.new_tag('span', attrs={'class': 'news-timeline-arrow', 'aria-hidden': 'true'})
 icon.string = '↗'
 preview.extend([image, icon])
 layout.extend([entries, preview])
 section.clear()
 section.extend([header, layout])

R=Path(__file__).parent
footer_nav = json.loads((R/'dist'/'site-catalog.json').read_text(encoding='utf8'))['navigation']
for f in (R/'dist').rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not s.select_one('.site-header'):continue
 old_footer = s.select_one('body > footer.bts-footer')
 if old_footer is not None:
  language = 'en' if s.html.get('lang') == 'en' else 'th'
  old_footer.replace_with(BeautifulSoup(footer(language, footer_nav[language]), 'html.parser'))
 for section in s.select('section.related-pages, section#related-information'):
  section.decompose()
 for n in s.select('link[href^="/bts-editorial.css"]'):n.decompose()
 body_path = s.body.get('data-path', '') if s.body else ''
 stylesheet_version = 60 if body_path in ('/th/home', '/en/home') else 56
 s.head.append(s.new_tag('link',rel='stylesheet',href=f'/bts-editorial.css?v={stylesheet_version}'))
 # Turn the homepage sustainability module into a full-bleed editorial scene.
 if body_path in ('/th/home', '/en/home'):
  metro_script = s.select_one('script[src^="/metro.js"]')
  if metro_script is not None:
   metro_script['src'] = '/metro.js?v=13'
  hero = s.select_one('.hero')
  if hero:
   tagline = hero.select_one('.hero-signature')
   if tagline is not None:
    tagline.decompose()
   video_control = hero.select_one('.hero-bottom')
   if video_control is not None:
    video_control.decompose()
  apply_finance_scene(s, body_path.split('/')[1])
  apply_investor_hub(s)
  apply_investor_overview(s, body_path.split('/')[1])
  apply_news_timeline(s, body_path.split('/')[1], R/'dist')
  # The newsletter/IR contact tiles are redundant after the homepage story flow.
  for section in s.select('main > .planb-contact'):
   section.decompose()
  scene = s.select_one('section#sustainability, section.sustainability')
  if scene:
   is_th = s.html.get('lang', 'th') == 'th'
   heading = 'การพัฒนาอย่างยั่งยืน' if is_th else 'Sustainable Development'
   description = ('เรามุ่งสร้างคุณค่าระยะยาว ด้วยการดำเนินธุรกิจที่รับผิดชอบต่อสิ่งแวดล้อม สังคม และการกำกับดูแลกิจการที่ดี'
                  if is_th else 'We create long-term value through responsible business practices for the environment, society and good corporate governance.')
   link_text = 'สำรวจความยั่งยืน' if is_th else 'Explore sustainability'
   link_href = '/th/sustainability/sustainability-at-bts-group/' if is_th else '/en/sustainability/sustainability-at-bts-group/'
   scene.clear()
   scene['class'] = ['sustainability-feature']
   scene['aria-labelledby'] = 'sustainability-cover-title'
   content = s.new_tag('div', attrs={'class': 'sustainability-feature-copy'})
   title = s.new_tag('h2', id='sustainability-cover-title')
   title.string = heading
   copy = s.new_tag('p')
   copy.string = description
   cta = s.new_tag('a', href=link_href, attrs={'class': 'sustainability-feature-action'})
   cta.string = link_text
   image = s.new_tag('img', src='/assets/sustainability-bangkok-sunset.webp', alt='', width='2172', height='724',
                     loading='lazy', decoding='async', attrs={'class': 'sustainability-feature-image'})
   content.extend([title, copy, cta])
   scene.extend([content, image])
 # Keep archive artwork restrained: show one representative story image per
 # news archive, and leave the remaining cards as clean editorial text cards.
 news_archive = s.body and s.body.get('data-path', '').endswith(('/news-event', '/update/news-event'))
 boxes = s.select('.source-body .card-bg')
 if news_archive:
  for box in boxes:
   for image in box.select('img'): image.decompose()
  boxes = boxes[:1]
 for box in boxes:
  if box.select_one('img'): continue
  a=box.find_parent('a',href=True)
  if not a:continue
  target=R/'dist'/a['href'].strip('/')/'index.html'
  if not target.is_file():continue
  source=BeautifulSoup(target.read_text(encoding='utf8'),'html.parser')
  photo=source.select_one('.source-body img[src]')
  if photo:
   img=s.new_tag('img',src=photo['src'],alt='',loading='eager')
   box.append(img)
 style_action_buttons(s)
 f.write_text(str(s),encoding='utf8')
print('Applied the BTS editorial system to all shared layouts.')
