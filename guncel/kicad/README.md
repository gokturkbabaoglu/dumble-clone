# Kart v5 (güncel) — KiCad 10

KiCad projesi: `amfi_yeni.kicad_pro` (dosya adları masaüstündeki `amfi_yeni_kart` projesiyle aynı tutuldu). Tek yüzlü (yalnız B.Cu), 185 × 96 mm. Devre: `eski/v2_v3/araclar/design2.py` netlisti (kart v4 ile aynı devre, Rev 5 + RV4 DRIVE).

**Durum:** şema ERC 0 hata / 0 uyarı; yerleşim ve 0,4 mm ince yollar hazır. **Açık:** 2 bağlantı çizilmedi (U2.4–TOUT, R22–R31); yollar elle kalınlaştırılacak. Tel köprü yok (yalnız JP1 giriş susturma köprüsü).

| Dosya | İçerik |
|---|---|
| `amfi_yeni.kicad_sch` | Tellerle çizilmiş şema, KiCad standart sembolleri |
| `amfi_yeni.pretty/` | Büyük padli ayak izleri (16 standart kopya + 6 özel) |
| `amfi_yeni.kicad_pcb` | Yerleşim + ince yollar (0,4 mm, boşluk 0,4 mm) |

Üretim sırası (betikler):

1. `gen_sema.py` — şema (netlist + semboller `gen_sch.py`), `check_sch.py` bağlantı denetimi
2. `gen_fp.py` — ayak izi kütüphanesi (pad ≥ 3,2 mm, padler arası ≥ 0,6 mm)
3. `gen_pcb.py [ESKİ_KART.kicad_pcb]` — yerleşim; varsayılan olarak kart v4'ün (`eski/v4_kicad_185x96/amfi/amfi.kicad_pcb`) parça konumlarına oturtur
4. `router.py` — tek katlı ızgara yönlendirici (PathFinder), `smooth.py` — merdivenleri düzeltme + onarım
5. `yk_drc.py`, `baglanti.py` — boşluk ve bağlantı denetimi, `render_pcb.py` — önizleme

Not: Yeniden üretmek, KiCad'de yapılan elle düzenlemelerin üzerine yazar.
