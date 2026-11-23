from pathlib import Path
import re

from bs4 import BeautifulSoup


BUTTON_LINKS = (
 'a.outline-button, a.official-action, a.btn, a.btn-back, a.finance-glass-action, '
 'a.investor-night-action, a.hero-discover, a.inner-content-link, a.chapter-back, '
 'a.card-link--icon-next, .footer-signature > a, button.archive-more'
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

R=Path(__file__).parent
for f in (R/'dist').rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not s.select_one('.site-header'):continue
 for n in s.select('link[href^="/bts-editorial.css"]'):n.decompose()
 body_path = s.body.get('data-path', '') if s.body else ''
 stylesheet_version = 46
 s.head.append(s.new_tag('link',rel='stylesheet',href=f'/bts-editorial.css?v={stylesheet_version}'))
 # Turn the homepage sustainability module into a full-bleed editorial scene.
 if body_path in ('/th/home', '/en/home'):
  metro_script = s.select_one('script[src^="/metro.js"]')
  if metro_script is not None:
   metro_script['src'] = '/metro.js?v=12'
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
  # The newsletter/IR contact tiles are redundant after the homepage story flow.
  for section in s.select('main > .planb-contact'):
   section.decompose()
  scene = s.select_one('.sustainability')
  if scene:
   is_th = s.html.get('lang', 'th') == 'th'
   heading = 'การพัฒนาอย่างยั่งยืน' if is_th else 'Sustainable Development'
   eyebrow = 'BTS GROUP  /  ความยั่งยืน' if is_th else 'BTS GROUP  /  SUSTAINABILITY'
   description = ('เรามุ่งสร้างคุณค่าระยะยาว ด้วยการดำเนินธุรกิจที่รับผิดชอบต่อสิ่งแวดล้อม สังคม และการกำกับดูแลกิจการที่ดี'
                  if is_th else 'We create long-term value through responsible business practices for the environment, society and good corporate governance.')
   link_text = 'สำรวจความยั่งยืน' if is_th else 'Explore sustainability'
   link_href = '/th/sustainability/sustainability-at-bts-group/' if is_th else '/en/sustainability/sustainability-at-bts-group/'
   scene.clear()
   scene['class'] = ['sustainability', 'sustainability-cover']
   scene['aria-labelledby'] = 'sustainability-cover-title'
   content = s.new_tag('div', attrs={'class': 'sustainability-cover-content'})
   label = s.new_tag('span', attrs={'class': 'sustainability-cover-eyebrow'})
   label.string = eyebrow
   title = s.new_tag('h2', id='sustainability-cover-title')
   title.string = heading
   copy = s.new_tag('p')
   copy.string = description
   cta = s.new_tag('a', href=link_href, attrs={'class': 'sustainability-cover-arrow', 'aria-label': link_text})
   arrow = s.new_tag('span', attrs={'aria-hidden': 'true'})
   arrow.string = '→'
   cta.append(arrow)
   links = s.new_tag('nav', attrs={'class': 'sustainability-cover-more', 'aria-label': 'Sustainability topics' if not is_th else 'หัวข้อความยั่งยืน'})
   destinations = [('sustainability/environmental-sustainability', 'ความยั่งยืนด้านสิ่งแวดล้อม' if is_th else 'Environmental Sustainability'),
                   ('sustainability/social-sustainability', 'ความยั่งยืนด้านสังคม' if is_th else 'Social Sustainability'),
                   ('corporate-governance/at-a-glance', 'การกำกับดูแลกิจการ' if is_th else 'Corporate Governance')]
   for index, (path, text) in enumerate(destinations):
    item = s.new_tag('a', href=f'/{s.html.get("lang", "th")}/{path}/', attrs={'data-esg': str(index)})
    item.string = text
    links.append(item)
   content.extend([label, title, copy, cta, links])
   scene.append(content)
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
