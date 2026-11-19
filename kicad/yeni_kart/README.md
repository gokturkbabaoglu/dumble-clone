# Yeni kart (amfi_yeni) — KiCad 10

Tek yüzlü (yalnız B.Cu), 185 × 96 mm. Devre: `tools/design2.py` netlisti (eski `kicad/amfi` ile aynı).

| Dosya | İçerik |
|---|---|
| `amfi_yeni.kicad_sch` | Tellerle çizilmiş şema, KiCad standart sembolleri |
| `amfi_yeni.pretty/` | Büyük padli ayak izleri (16 standart kopya + 6 özel) |
| `amfi_yeni.kicad_pcb` | Yerleşim + ince yollar (0,4 mm, boşluk 0,4 mm) |

Üretim sırası (betikler):

1. `gen_sema.py` — şema (netlist + semboller `gen_sch.py`), `check_sch.py` bağlantı denetimi
2. `gen_fp.py` — ayak izi kütüphanesi (pad ≥ 3,2 mm, padler arası ≥ 0,6 mm)
3. `gen_pcb.py ESKİ_KART.kicad_pcb` — yerleşim (eski kartın konumlarına oturtma)
4. `router.py` — tek katlı ızgara yönlendirici (PathFinder), `smooth.py` — merdivenleri düzeltme + onarım
5. `yk_drc.py`, `baglanti.py` — boşluk ve bağlantı denetimi, `render_pcb.py` — önizleme

Not: Yeniden üretmek, KiCad'de yapılan elle düzenlemelerin üzerine yazar.
