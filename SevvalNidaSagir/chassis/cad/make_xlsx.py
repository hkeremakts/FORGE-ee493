import sys
sys.path.insert(0, ".")
from bom import BOM
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation

F = "Arial"
wb = Workbook()
ws = wb.active
ws.title = "Malzeme Listesi"
thin = Side(style="thin", color="BFBFBF")
B = Border(bottom=thin)
head_fill = PatternFill("solid", fgColor="1F3A5F")
yellow = PatternFill("solid", fgColor="FFFF00")
grp_fill = {"Hareket": "E8F0FA", "Vida": "F2F2F2", "Baskı": "FFF2E5", "Kablo": "F2F2F2", "Güç": "EAF5EC", "Diğer": "F7EEF8"}

ws["A1"] = "RAPTOR · Araç Hareketi · Alınacak malzemeler"
ws["A1"].font = Font(name=F, size=14, bold=True)
ws["A2"] = "Hazırlayan: Şevval Nida Sağır · 18.11.2026 · Sarı hücrelere fiyat yaz, Toplam kendiliğinden hesaplanır. Durum sütunu açılır listeden seçilir."
ws["A2"].font = Font(name=F, size=9, italic=True, color="555555")

hdr = ["No", "Grup", "Malzeme", "Özellik / not", "Adet", "Nereden", "Link", "Durum", "Sorumlu", "Birim fiyat (TL)", "Toplam (TL)"]
R0 = 4
for c, h in enumerate(hdr, 1):
    cell = ws.cell(R0, c, h)
    cell.font = Font(name=F, bold=True, color="FFFFFF", size=10)
    cell.fill = head_fill
    cell.alignment = Alignment(vertical="center", wrap_text=True)
ws.row_dimensions[R0].height = 22

r = R0
for i, (grp, name, note, qty, src, status, owner, link, price) in enumerate(BOM, 1):
    r = R0 + i
    vals = [i, grp, name, note, qty, src, link, status, owner, price, f'=IF(J{r}="","",E{r}*J{r})']
    for c, v in enumerate(vals, 1):
        cell = ws.cell(r, c, v)
        cell.font = Font(name=F, size=10, color="0000FF" if c in (5, 10) and v not in (None, "") else "000000")
        cell.border = B
        cell.alignment = Alignment(vertical="top", wrap_text=c in (3, 4, 6))
        cell.fill = PatternFill("solid", fgColor=grp_fill[grp])
    ws.cell(r, 10).fill = yellow
    ws.cell(r, 10).number_format = '#,##0.00'
    ws.cell(r, 11).number_format = '#,##0.00'
    if link:
        ws.cell(r, 7).hyperlink = link
        ws.cell(r, 7).value = link.split("//")[1].split("/")[0]
        ws.cell(r, 7).font = Font(name=F, size=10, color="0563C1", underline="single")
    if price:
        ws.cell(r, 10).comment = Comment(f"Kaynak: {src} ürün sayfası, 18.11.2026 gece görülen KDV dahil fiyat. Almadan önce kontrol et.", "Şevval")
last = r

tr = last + 2
ws.cell(tr, 9, "Alınacakların toplamı").font = Font(name=F, bold=True)
ws.cell(tr, 11, f'=SUMIFS(K{R0+1}:K{last},H{R0+1}:H{last},"Alınacak")').font = Font(name=F, bold=True)
ws.cell(tr, 11).number_format = '#,##0.00'
ws.cell(tr + 1, 9, "Fiyatı girilmemiş (Alınacak)").font = Font(name=F, size=9, color="555555")
ws.cell(tr + 1, 11, f'=COUNTIFS(H{R0+1}:H{last},"Alınacak",J{R0+1}:J{last},"")').font = Font(name=F, size=9, color="555555")

dv = DataValidation(type="list", formula1='"Alınacak,Sipariş verildi,Geldi,Var,Kontrol et"', allow_blank=True)
ws.add_data_validation(dv)
dv.add(f"H{R0+1}:H{last}")

for col, w in zip("ABCDEFGHIJK", [5, 10, 36, 44, 6, 26, 18, 13, 13, 14, 13]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = ws.cell(R0 + 1, 4)
ws.auto_filter.ref = f"A{R0}:K{last}"

# ---- Basılacaklar ----
p = wb.create_sheet("Basılacaklar (3D)")
p["A1"] = "3D baskı parçaları (PETG) · dosyalar: 03_Sase_3D/stl"
p["A1"].font = Font(name=F, size=13, bold=True)
ph = ["Parça", "Dosya", "Adet", "Baskı notu"]
rows = [
    ("Alt plaka", "alt_plaka.stl", 1, "Düz, 4 duvar, %30 dolgu"),
    ("Üst plaka", "ust_plaka.stl", 1, "Ayaklar yukarı, 4 duvar, %30 dolgu"),
    ("Motor braketi", "motor_braketi.stl", 2, "Dış yüz tablaya, 5 duvar, %50 dolgu, destek yok"),
    ("Kat direği", "kat_diregi.stl", 6, "Dik, 4 duvar"),
    ("Kamera direği", "kamera_diregi.stl", 1, "Dik (150 mm)"),
    ("Direk ucu (kamera + UWB)", "direk_ucu_kamera_uwb.stl", 1, "Kamera plakasının ön yüzü tablaya"),
    ("Sarhoş pulu 0,5 mm", "sarhos_pulu_0_5mm.stl", 2, "Sarhoş yüksekliği ince ayar"),
    ("Sarhoş pulu 1 mm", "sarhos_pulu_1mm.stl", 2, "Pololu 953 + 1 mm = 14,5 mm"),
]
for c, h in enumerate(ph, 1):
    cell = p.cell(3, c, h); cell.font = Font(name=F, bold=True, color="FFFFFF"); cell.fill = head_fill
for i, row in enumerate(rows, 4):
    for c, v in enumerate(row, 1):
        cell = p.cell(i, c, v); cell.font = Font(name=F, size=10); cell.border = B
p.cell(i + 1, 1, "Toplam parça").font = Font(name=F, bold=True)
p.cell(i + 1, 3, f"=SUM(C4:C{i})").font = Font(name=F, bold=True)
p.cell(i + 2, 1, "Tahmini filament: 250-300 g PETG").font = Font(name=F, size=9, italic=True, color="555555")
for col, w in zip("ABCD", [26, 28, 7, 48]):
    p.column_dimensions[col].width = w

wb.save("doc/02_Malzeme_Listesi.xlsx")
print("rows", len(BOM))
