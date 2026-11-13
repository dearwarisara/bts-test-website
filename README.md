# BTS Group website

เว็บไซต์ BTS Group ภาษาไทยและอังกฤษ ใช้ฟอนต์ OzoneX และ Mulish ของ BTS พร้อมเอกลักษณ์ขาว–น้ำเงิน–แดง เส้นราง และจุดเชื่อมต่อสถานี

## เปิดเว็บไซต์

```sh
npm start
```

เปิด http://127.0.0.1:4173/ โดยใช้ Node.js 18 ขึ้นไป ไม่ต้องติดตั้ง dependencies สำหรับการรันเว็บไซต์

GitHub Pages: https://dearwarisara.github.io/bts-test-website/

## หน้าเว็บและเมนู

- ทั้ง 1,002 หน้าใช้หัวเว็บ เมนู และท้ายเว็บร่วมกัน
- เมนูใช้ชื่อ ลำดับ และเมนูย่อยจากโครงสร้าง BTS ใน site-catalog.json
- เมนู ผลค้นหา และลิงก์เนื้อหาที่มีหน้าในเว็บเรา เชื่อมไปยังเส้นทางภายใน
- ภาษา TH/EN เชื่อมหน้าคู่ภาษาในเว็บเรา
- หน้าแรกแสดงข่าวล่าสุด ข้อมูลสำคัญทางการเงิน เอกสารเผยแพร่ ธุรกิจ และความยั่งยืนของ BTS
- เนื้อหา ตาราง ข่าว และเอกสารของหน้าภายในคงข้อมูลต้นฉบับไว้
- ไฟล์ดาวน์โหลด วิดีโอ และสื่อที่โฮสต์โดย BTS ใช้แหล่งต้นฉบับ

## สร้างและตรวจเว็บไซต์

เครื่องมือสร้างใช้ Python และ Beautiful Soup โดยเว็บไซต์ที่พร้อมรันอยู่ใน dist/ แล้ว

```sh
npm run build:site
npm run audit:site
npm test
npm run build:pages
```

unify_bts_site.py สร้างหน้าแรกจากข้อมูล BTS และใช้ shell / ฟอนต์ / ธีมเดียวกันกับทุกหน้า พร้อมปรับลิงก์ต้นฉบับให้ตรงกับ route ภายใน

audit_bts_site.py ตรวจทุกหน้า ทั้งโครงสร้างเมนู ลิงก์ภายใน และเนื้อหาหน้าภายในเทียบกับ Git HEAD แล้วเขียนผลใน site-unification-report.json

## โครงสร้างสำคัญ

- dist/metro.css และ dist/metro.js: โครงสร้างและการทำงานร่วมกันของเว็บไซต์
- dist/bts-brand.css: ฟอนต์ BTS สี และรายละเอียดเอกลักษณ์
- dist/bts-inner.css: หัวเว็บร่วม หน้าภายใน ตาราง เอกสาร และ responsive layout
- dist/content.js: ค้นหาในหน้า คลังเอกสาร และแท็บของเนื้อหา
- dist/site-catalog.json: ข้อมูลหน้า route และโครงสร้างเมนู BTS
- navigation-tree.json: โครงสร้างเมนูต้นฉบับ
- build_metro_home.py: ข้อมูลและโครงสร้างหน้าแรกก่อนใช้ shared shell

เมื่อสร้างข้อมูลจาก build_pages.py ใหม่ ให้รัน npm run build:site ต่อเพื่อใช้ธีมร่วมเวอร์ชันปัจจุบัน

## เผยแพร่

Push main แล้ว GitHub Actions จะตรวจและจัดแพ็กด้วย build-pages.mjs ก่อนเผยแพร่ GitHub Pages อัตโนมัติ โดยปรับเส้นทางไฟล์ให้รองรับ /bts-test-website/

ข้อมูลและสื่ออ้างอิง https://www.btsgroup.co.th/th/home ส่วนแนวทางการจัดวางเริ่มต้นอ้างอิง https://www.metrosystems.co.th/en/home
