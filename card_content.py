"""Shared presentation data for generated navigation cards."""
import re
IMAGES={
 'our-business/business-overview':'https://www.btsgroup.co.th/storage/banner/banner-about.jpg',
 'our-business/move':'https://www.btsgroup.co.th/storage/business/move/rail-business.jpg',
 'our-business/mix':'https://www.btsgroup.co.th/storage/business/mix/advertising.jpg',
 'our-business/match':'https://www.btsgroup.co.th/storage/business/match/mixed-use.webp',
}
def card_image(page):
 key='/'.join(page.get('path',page.get('href','')).strip('/').split('/')[1:])
 return IMAGES.get(key,page.get('image',''))
def summarize(value,limit=180):
 value=' '.join(str(value or '').split())
 if len(value)<=limit:return value
 for m in re.finditer(r'[.!?](?=\s|$)',value):
  if 50<=m.end()<=220:return value[:m.end()]
 cut=value[:limit].rsplit(' ',1)[0]
 if len(cut)<limit*.6:cut=value[:limit]
 return cut.rstrip(' ,;:-')+'…'
