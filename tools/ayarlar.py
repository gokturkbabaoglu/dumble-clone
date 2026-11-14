"""Arama ayarları. Program bunları ayarlar.json dosyasından okur; arayüzden değiştirilir."""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
YOL = os.path.join(DIR, 'ayarlar.json')
VARSAYILAN = {
    'kart_eni': 185,            # 165 veya 185 (mm)
    'jcost': 150,               # yol çizicide tel köprü maliyeti (yüksek = köprüden kaçın)
    'jmax': 8,                  # en uzun köprü (hücre; 1 hücre = 1.27 mm)
    'ring': 2,                  # arka/sol/sağ kenarda GND şeridi (hücre; 0 = yok)
    'kopru_agirlik': 60,        # puanda her köprünün cezası
    'kotu_kopru_agirlik': 100,  # parça gövdesi üzerinden geçen köprü cezası
    'zincir': 10,               # aynı anda çalışan arama zinciri (çekirdek sayısı kadar)
    'deneme': 3000,             # zincir başına bir turdaki deneme sayısı
    'sicaklik_bas': 8.0,
    'sicaklik_son': 0.3,
}
# Bu anahtarlar değişirse kayıtlı zincir durumları geçersiz olur (kart/puan değişir)
ONEMLI = ('kart_eni', 'jcost', 'jmax', 'ring', 'kopru_agirlik', 'kotu_kopru_agirlik')

def oku():
    d = dict(VARSAYILAN)
    try:
        with open(YOL, encoding='utf-8') as f: d.update(json.load(f))
    except Exception:
        pass
    return d

def yaz(d):
    with open(YOL, 'w', encoding='utf-8') as f: json.dump(d, f, indent=1, ensure_ascii=False)

def imza(d):
    return '|'.join(f'{k}={d[k]}' for k in ONEMLI)

A = oku()
