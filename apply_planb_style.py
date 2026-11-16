"""Apply Plan B-inspired presentation while preserving BTS content and fonts."""
from pathlib import Path
from bs4 import BeautifulSoup
import re,subprocess,sys
R=Path(__file__).parent;D=R/'dist'
for file in D.rglob('*.html'):
 source=file.read_text(encoding='utf-8-sig')
 home=file in (D/'index.html',D/'th/home/index.html',D/'en/home/index.html')
 if home:
  s=BeautifulSoup(source,'html.parser');lang='en' if s.html.get('lang')=='en' else 'th'
  hero=s.select_one('.hero')
  # Keep the original headline over full-size video without scroll scaling.
  if hero:
   screen=hero.select_one('.hero-screen')
   if screen:
    children=list(screen.contents)
    hero.clear()
    for child in children:hero.append(child)
   for node in hero.select('.hero-brand-copy,.hero-bottom>a'):node.decompose()
   hero['aria-label']='BTS Group corporate video' if lang=='en' else 'วิดีโอแนะนำ BTS Group'
   copy=s.new_tag('div',attrs={'class':'hero-brand-copy'})
   title=s.new_tag('h1',attrs={'aria-label':'Borderless Transform Solutions'})
   for line in ('B orderless','T ransform','S olutions'):
    span=s.new_tag('span');span.string=line;title.append(span)
   copy.append(title);hero.append(copy)

  main=s.main;financial=s.select_one('.financial-home');pub=s.select_one('#publications');news=s.select_one('#news');shortcuts=s.select_one('.home-shortcuts')
  if financial and shortcuts:shortcuts.insert_after(financial.extract())
  if financial and pub:financial.insert_after(pub.extract())
  if pub and news:pub.insert_after(news.extract())
  if shortcuts:shortcuts.decompose()
  business=s.select_one('#business')
  if business:
   old=business.select_one('.network-line')
   if old:old.decompose()
   intro=business.select_one('.business-intro>p')
   if intro:intro.string='Three core businesses: MOVE, MIX and MATCH — connecting mobility, marketing and business opportunities.' if lang=='en' else 'สามธุรกิจหลัก MOVE, MIX และ MATCH เชื่อมต่อการเดินทาง การตลาด และโอกาสทางธุรกิจ'
   panels=business.select_one('.business-panels');panels.clear()
   entries=[('move','MOVE','การเดินทางและระบบขนส่ง','Mobility and transportation','move/rail-business.jpg'),('mix','MIX','สื่อโฆษณาและการตลาด','Media and marketing','mix/advertising.jpg'),('match','MATCH','พันธมิตรและการลงทุน','Partnerships and investments','match/mixed-use.webp')]
   for slug,title,th,en,photo in entries:
    a=s.new_tag('a',href=f'/{lang}/our-business/{slug}/',attrs={'class':'business-panel','data-business':slug,'style':f'--panel-image:url(https://www.btsgroup.co.th/storage/business/{photo})'})
    h=s.new_tag('h3');h.string=title;a.append(h)
    desc=s.new_tag('span',attrs={'class':'business-description'});desc.string=en if lang=='en' else th;a.append(desc)
    arrow=s.new_tag('span',attrs={'class':'panel-arrow','aria-hidden':'true'});arrow.string='↗';a.append(arrow);panels.append(a)
  tabs=s.select_one('.esg-tabs')
  if tabs:
   tabs.clear()
   entries=[('sustainability/environmental-sustainability','ความยั่งยืนด้านสิ่งแวดล้อม','Environmental Sustainability'),('sustainability/social-sustainability','ความยั่งยืนด้านสังคม','Social Sustainability'),('corporate-governance/at-a-glance','การกำกับดูแลกิจการ','Corporate Governance')]
   for i,(path,th,en) in enumerate(entries):
    a=s.new_tag('a',href=f'/{lang}/{path}/',attrs={'data-esg':str(i),'class':'active' if i==0 else ''})
    small=s.new_tag('small');small.string=f'{i+1:02d}';a.append(small)
    label=s.new_tag('span');label.string=en if lang=='en' else th;a.append(label)
    arrow=s.new_tag('b',attrs={'aria-hidden':'true'});arrow.string='→';a.append(arrow);tabs.append(a)
   caption=s.select_one('#esg-caption');caption.string=('Environmental Sustainability' if lang=='en' else 'ความยั่งยืนด้านสิ่งแวดล้อม')+' ↗'
   s.select_one('#esg-image')['alt']='Environmental Sustainability' if lang=='en' else 'ความยั่งยืนด้านสิ่งแวดล้อม'

  if pub and not pub.select_one('.publication-body'):
   body=s.new_tag('div',attrs={'class':'publication-body'})
   reports=pub.select_one('.bts-reports');resources=pub.select_one('.ir-layout');bottom=pub.select_one('.ir-bottom')
   if reports:
    tabs=s.new_tag('div',attrs={'class':'report-tabs','role':'group','aria-label':'Reports' if lang=='en' else 'รายงาน'})
    for i,label in enumerate(('Annual Report','Sustainability Report') if lang=='en' else ('รายงานประจำปี','รายงานความยั่งยืน')):
     button=s.new_tag('button',attrs={'data-report-tab':str(i),'aria-pressed':'true' if i==0 else 'false','class':'active' if i==0 else ''});button.string=label;tabs.append(button)
    reports.insert(0,tabs)
    for i,card in enumerate(reports.select('.annual-card')):card['data-report-card']=str(i)
    body.append(reports.extract())
   if resources:body.append(resources.extract())
   if bottom:body.append(bottom.extract())
   pub.append(body)
  if not s.select_one('.planb-contact'):
   contact=s.new_tag('section',attrs={'class':'planb-contact container'})
   entries=[('อีเมล์รับข่าวสาร','ติดตามข่าวสารและความเคลื่อนไหวของ BTS Group','สมัครรับข่าวสาร','information-inquiry/news-subscription','banner-about.jpg'),('ติดต่อนักลงทุนสัมพันธ์','ข้อมูลและช่องทางติดต่อฝ่ายนักลงทุนสัมพันธ์','ติดต่อเรา','information-inquiry/ir-contact','banner-ir.jpg')]
   if lang=='en':entries=[('Email Alerts','Stay connected with the latest news from BTS Group.','Subscribe','information-inquiry/news-subscription','banner-about.jpg'),('IR Contact','Investor information and IR contact channels.','Contact Us','information-inquiry/ir-contact','banner-ir.jpg')]
   for i,(heading,desc,cta,path,image) in enumerate(entries):
    a=s.new_tag('a',href=f'/{lang}/investor-relations/{path}/',attrs={'class':'contact-tile contact-tile-'+str(i)})
    img=s.new_tag('img',src='https://www.btsgroup.co.th/storage/banner/'+('banner-about.jpg' if i==0 else 'banner-ir.jpg'),alt='',loading='lazy');a.append(img)
    h=s.new_tag('h2');h.string=heading;a.append(h)
    p=s.new_tag('p');p.string=desc;a.append(p)
    span=s.new_tag('span');span.string=cta+' ↗';a.append(span);contact.append(a)
   main.append(contact)
  source=str(s)
 source=re.sub(r'<span class="header-context">BTS GROUP</span>','',source)
 source=re.sub(r'/content\.js\?v=\d+','/content.js?v=12',source)
 source=re.sub(r'/metro\.js\?v=\d+','/metro.js?v=11',source)
 # A single stylesheet updates the shared shell and all content layouts.
 source=re.sub(r'<link[^>]+href="/planb-style\.css[^\"]*"[^>]*>','',source)
 source=re.sub(r'<link[^>]+href="/bts-quality\.css[^\"]*"[^>]*>','',source)
 source=source.replace('</head>','<link rel="stylesheet" href="/planb-style.css?v=9"/><link rel="stylesheet" href="/bts-quality.css?v=12"/></head>')
 source=re.sub(r'<script[^>]+src="/planb-motion\.js[^\"]*"[^>]*>\s*</script>','',source)
 if home:source=source.replace('</body>','<script type="module" src="/planb-motion.js?v=2"></script></body>')

 file.write_text(source,encoding='utf-8')
print('Applied Plan B-inspired styling to all pages; BTS content and local routes preserved.')


subprocess.run([sys.executable,str(R/'repair_cards.py')],check=True)

subprocess.run([sys.executable,str(R/'redesign_history.py')],check=True)
