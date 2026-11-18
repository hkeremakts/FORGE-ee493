"""RAPTOR araç: alınacak malzemeler (PDF ve Excel aynı listeden üretilir)."""

BOM_COLUMNS = ["Grup", "Malzeme", "Özellik / not", "Adet", "Nereden", "Durum", "Sorumlu",
               "Link", "Birim fiyat (TL)"]

DIRENC_MOTOR = "https://www.direnc.net/jgb37-520-12v-530rpm-enkoderli-motor"
ROBOTISTAN_BTS = "https://www.robotzade.com/urun/bts7960b-20-amper-motor-surucu-karti"
ROBOTZADE_ESP = "https://www.robotzade.com/urun/esp32-devkit-v1-wifi-bluetooth-gelistirme-karti-lehimsiz-30-pin"
MOTOROBIT_TEKER = "https://www.motorobit.com/65x27-tekerlek-kirmizi"
MOTOROBIT_KAPLIN = "https://www.motorobit.com/hex-wheel-coupling-compatible-with-6mm-motor-shaft"
DIRENC_SARHOS = "https://www.direnc.net/sarhos-teker-ball-caster-with-12-metal-ball-pololu"

# (grup, malzeme, not, adet, nereden, durum, sorumlu, link, birim fiyat)
BOM = [
    # ---- Hareket ----
    ("Hareket", "JGB37-520 12V 530 rpm enkoderli motor", "1:19 redüktör, Hall enkoder A/B. 2 + 1 yedek", 3,
     "Direnc.net (DSTK22441)", "Sipariş verildi", "Şevval", DIRENC_MOTOR, 665.41),
    ("Hareket", "BTS7960B motor sürücü (20 A sürekli)", "Kart başına 1 motor. 2 + 1 yedek (isteğe bağlı)", 2,
     "Robotzade", "Alınacak", "Şevval", ROBOTISTAN_BTS, 275.40),
    ("Hareket", "ESP32 DevKit V1 30 pin (lehimsiz)", "Pin başlıkları lehimlenecek. 1 (+1 yedek isteğe bağlı)", 1,
     "Robotzade", "Alınacak", "Şevval", ROBOTZADE_ESP, 367.20),
    ("Hareket", "Teker 65 × 27 mm (Motorobit)", "Düz lastik, 2 aynı renk. Kaplin uyumunu sor", 2,
     "Motorobit", "Alınacak", "Şevval", MOTOROBIT_TEKER, 309.00),
    ("Hareket", "6 mm mil hex teker kaplini", "12 mm altıgen, 30 mm boy, tekerle 6 mm gelmezse", 2,
     "Motorobit", "Alınacak", "Şevval", MOTOROBIT_KAPLIN, 123.60),
    ("Hareket", "Pololu #953 sarhoş (1/2\" metal bilya)", "Yükseklik 13,5 mm + 1 mm pul. B: 2, A: 1", 2,
     "Direnc.net / Pololu bayileri", "Alınacak", "Şevval", DIRENC_SARHOS, None),
    # ---- Vida ----
    ("Vida", "M3×8 vida", "Motor → braket (12) + direk sıkıştırma (1) + yedek", 15,
     "Hırdavatçı / Robotistan", "Alınacak", "Şevval", "", None),
    ("Vida", "M3×16 vida + somun", "Braket → alt plaka", 8,
     "Hırdavatçı / Robotistan", "Alınacak", "Şevval", "", None),
    ("Vida", "M3×10 vida", "Kat direkleri (6 direk × 2)", 12,
     "Hırdavatçı / Robotistan", "Alınacak", "Şevval", "", None),
    ("Vida", "M2.5×6 vida", "Raspberry Pi 5", 4,
     "Robotistan", "Alınacak", "Pi ekibi", "", None),
    ("Vida", "M2×8 vida + somun", "Pi Camera 3 (4) + Pololu sarhoş (4, pul ile)", 8,
     "Robotistan", "Alınacak", "Şevval", "", None),
    ("Vida", "M3 aralayıcı (standoff) seti", "Naylon/pirinç 6-10 mm; BTS7960, ESP32, XL4015 için", 1,
     "Robotistan", "Alınacak", "Şevval", "", None),
    # ---- Baskı ----
    ("Baskı", "PETG filament 1,75 mm", "Şase ~250-300 g; deneme baskılarıyla 1 kg", 1,
     "Filament satıcısı", "Alınacak", "Ekip", "", None),
    # ---- Kablo / küçük ----
    ("Kablo", "0,1 µF seramik kondansatör", "Motor uçlarına parazit için (motor başına 1-2)", 4,
     "Direnc.net", "Alınacak", "Şevval", "", None),
    ("Kablo", "100 kΩ + 22 kΩ direnç", "Batarya voltajını ESP32 ile ölçmek için bölücü", 2,
     "Direnc.net", "Alınacak", "Şevval", "", None),
    ("Kablo", "Jumper kablo seti (D-D, D-E)", "ESP32 ↔ BTS7960 ↔ enkoder", 1,
     "Robotistan", "Alınacak", "Şevval", "", None),
    ("Kablo", "18 AWG silikon kablo 1 m", "Batarya → sigorta → sürücüler. Eksiyi siyah bantla işaretle", 1,
     "Robotzade", "Alınacak", "Şevval", "", 39.78),
    ("Kablo", "Makaron + kablo bağı", "", 1,
     "Hırdavatçı", "Alınacak", "Ekip", "", None),
    # ---- Güç (Güneş'in raporundan) ----
    ("Güç", "Samsung 25R 18650 pil", "3S paket", 3, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "3S 18650 pil yuvası", "", 1, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "3S BMS", "", 1, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "Bıçak sigorta yuvası", "", 1, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "Ana anahtar", "", 1, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "XL4015 5 A voltaj düşürücü", "12 V → 5 V (Pi 5 için)", 1, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "XT60 konnektör", "", 1, "—", "Var", "Güç ekibi", "", None),
    ("Güç", "Bıçak sigorta", "Motor hattı için ~10 A", 3, "Oto yedek parça / Robotistan", "Alınacak", "Güç ekibi", "", None),
    ("Güç", "3S Li-ion şarj cihazı", "12,6 V", 1, "Robotistan", "Alınacak", "Güç ekibi", "", None),
    ("Güç", "Şarj soketi (DC jak)", "", 1, "Robotistan", "Alınacak", "Güç ekibi", "", None),
    ("Güç", "Elektrolitik kondansatör", "Sürücü girişine, 470-1000 µF 25 V", 2, "Direnc.net", "Alınacak", "Güç ekibi", "", None),
    # ---- Diğer ekipler ----
    ("Diğer", "Raspberry Pi 5", "Görüntü işleme", 1, "—", "Kontrol et", "Pi ekibi", "", None),
    ("Diğer", "Raspberry Pi Camera Module 3", "Direk ucuna, 21×12,5 M2", 1, "—", "Kontrol et", "Görüntü ekibi", "", None),
    ("Diğer", "UWB tag", "Direk ucundaki tablaya", 1, "—", "Kontrol et", "UWB ekibi", "", None),
    ("Diğer", "IMU", "Yön (alfa) için, isteğe bağlı", 1, "—", "Kontrol et", "Ekip", "", None),
]
