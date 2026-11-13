# BTS Group website redesign

เว็บไซต์ต้นแบบ BTS Group ภาษาไทยและอังกฤษ พร้อมโมเดลรถไฟ 3D และหน้าความเป็นมาแบบเลื่อนผ่านสถานีตามปี

## เว็บไซต์ public

<https://dearwarisara.github.io/bts-test-website/>

เมื่อ push ขึ้น `main` GitHub Actions จะ deploy ไป GitHub Pages อัตโนมัติ โดย `build-pages.mjs` ปรับลิงก์และเส้นทางไฟล์ให้รองรับ `/bts-test-website/` ส่วน `dist/` ยังใช้รันในเครื่องและโฮสต์ที่ root domain ได้ตามเดิม

## รันเว็บไซต์

ใช้ Node.js 18 ขึ้นไป ไม่ต้องติดตั้ง dependencies

```sh
git clone https://github.com/dearwarisara/bts-test-website.git
cd bts-test-website
npm start
```

- หน้าหลัก: <http://127.0.0.1:4173/>
- ความเป็นมา 3D: <http://127.0.0.1:4173/th/about/our-history/>
- ภาษาอังกฤษ: <http://127.0.0.1:4173/en/about/our-history/>

เลื่อนหน้าเพื่อให้รถไฟวิ่งอย่างต่อเนื่องผ่าน 21 หมุดหมาย หรือเลือกปีจากแถบด้านล่าง ฉากและองค์ประกอบรอบรางเปลี่ยนตามเหตุการณ์ มีปุ่มพักการเคลื่อนไหวและรองรับการตั้งค่าลดการเคลื่อนไหวของอุปกรณ์

กำหนด `PORT` และ `HOST` ผ่าน environment variables ได้หากต้องการเปลี่ยนพอร์ตหรือที่อยู่ของเซิร์ฟเวอร์

## โครงสร้าง

- `dist/` เว็บไซต์ที่พร้อมรันและนำไปโฮสต์แบบ static ได้ทันที
- `dist/history-world.js` ฉากและการเคลื่อนไหวในหน้าความเป็นมา
- `dist/history-world.css` เลย์เอาต์หน้าความเป็นมาสำหรับคอมและมือถือ
- `dist/details.js` โมเดลรถไฟที่ใช้ร่วมกับหน้าแรก
- `server.mjs` เซิร์ฟเวอร์สำหรับรันในเครื่อง
- `navigation-tree.json` ลำดับหมวดและเมนูย่อยจาก sitemap ทางการ ใช้ร่วมกันทั้งเมนูหลัก เมนูในหมวด และหน้า sitemap
- `extract_navigation.py` เครื่องมือดึงโครงสร้างเมนูจากไฟล์ sitemap ใน `.cache-bts/`
- `build_pages.py`, `inner_design.py`, `collect_pages.py` เครื่องมือรวบรวมและสร้างหน้าเว็บไซต์จากข้อมูลต้นฉบับ

ไฟล์ใน `dist/` สร้างไว้แล้ว การรันเว็บไซต์ไม่ต้องใช้ Python หรือข้อมูล cache ส่วนการสร้างหน้าจากต้นฉบับใหม่ต้องมี Python, Beautiful Soup และข้อมูลจาก `collect_pages.py` ใน `.cache-bts/`

เนื้อหา โลโก้ และฟอนต์อ้างอิง BTS Group ส่วนเอกสารและฟอร์มที่ต้องส่งข้อมูลเชื่อมต่อไปยังเว็บไซต์ทางการ
