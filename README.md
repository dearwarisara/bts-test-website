# BTS Group website

เว็บไซต์ BTS Group ที่ใช้เอกลักษณ์เส้นรางและจุดเชื่อมต่อ พร้อมสีขาว–น้ำเงิน–แดง ฟอนต์ OzoneX สำหรับภาษาไทย และ Mulish สำหรับหัวข้ออังกฤษ ตามเว็บไซต์ BTS Group ต้นฉบับ

## เปิดเว็บไซต์

- GitHub Pages: https://dearwarisara.github.io/bts-test-website/
- รันในเครื่องด้วย Node.js 18 ขึ้นไป ไม่ต้องติดตั้ง dependencies:

```sh
npm start
```

เปิด http://127.0.0.1:4173/

## หน้าแรกเวอร์ชันปัจจุบัน

- วิดีโอเปิดหน้าเต็มจอ พร้อมปุ่มหยุดและเล่น
- เมนูสองแถวและ mega menu พร้อมเมนูย่อยบนมือถือ
- แถบธุรกิจ BTS สี่หมวดตามข้อมูลหน้าแรกต้นฉบับ
- ข้อมูลสำคัญทางการเงิน รายงานประจำปี และลิงก์นักลงทุนสัมพันธ์
- ส่วนความยั่งยืนที่สลับรูปและลิงก์ตามหมวด
- ข่าวแบบเลื่อน พร้อมปุ่มก่อนหน้าและถัดไป
- ค้นหาจากข้อมูลหน้าเว็บไซต์ใน site-catalog.json
- รองรับการตั้งค่าลดการเคลื่อนไหวของอุปกรณ์

ไฟล์หน้าแรกคือ dist/index.html และ dist/th/home/index.html โดยใช้ dist/metro.css, dist/bts-brand.css และ dist/metro.js

สร้างหน้าแรกใหม่จากข้อมูลที่กำหนดใน build_metro_home.py ด้วย Python:

```sh
python build_metro_home.py
```

## เผยแพร่

Push branch main แล้ว GitHub Actions จะตรวจและจัดแพ็กด้วย build-pages.mjs ก่อนเผยแพร่ GitHub Pages อัตโนมัติ ตัวจัดแพ็กปรับเส้นทางไฟล์ให้รองรับ /bts-test-website/

```sh
npm run build:pages
```

หน้าเนื้อหาและเอกสารอื่นใน dist/ ยังคงเปิดได้ตามเส้นทางเดิม ส่วนลิงก์ข้อมูลจากหน้าแรกเชื่อมเว็บไซต์ BTS Group ต้นฉบับ

## แหล่งอ้างอิง

- ข้อมูลและสื่อ: https://www.btsgroup.co.th/th/home
- ต้นแบบเลย์เอาต์: https://www.metrosystems.co.th/en/home

