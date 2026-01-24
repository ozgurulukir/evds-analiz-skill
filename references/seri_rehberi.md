# EVDS Seri Rehberi

## ANAHTAR KELİME → SERİ EŞLEŞTİRME

Kullanıcı bu kelimeleri kullandığında ilgili serileri öner:

### Enflasyon / TÜFE / ÜFE
```python
ENFLASYON_SERILERI = {
    'TP.FG.J0': 'TÜFE - Genel Endeks (2003=100)',      # Aylık, format: 2024-1
    'TP.FG.J01': 'TÜFE - Gıda ve Alkolsüz İçecekler',  # Aylık, format: 2024-1
    'TP.FG.J02': 'TÜFE - Alkollü İçecekler ve Tütün',  # Aylık, format: 2024-1
    'TP.FG.J03': 'TÜFE - Giyim ve Ayakkabı',           # Aylık, format: 2024-1
    'TP.FG.J04': 'TÜFE - Konut',                       # Aylık, format: 2024-1
}
# NOT: TÜFE yıllık değişim için TP.FG.J0 çekip .pct_change(12)*100 hesapla
```

### Döviz / Kur / USD / EUR / Dolar / Euro
```python
DOVIZ_SERILERI = {
    'TP.DK.USD.A': 'USD - Döviz Alış',    # Günlük, format: 01-01-2024
    'TP.DK.USD.S': 'USD - Döviz Satış',   # Günlük, format: 01-01-2024
    'TP.DK.EUR.A': 'EUR - Döviz Alış',    # Günlük, format: 01-01-2024
    'TP.DK.EUR.S': 'EUR - Döviz Satış',   # Günlük, format: 01-01-2024
    'TP.DK.GBP.A': 'GBP - Döviz Alış',    # Günlük, format: 01-01-2024
    'TP.DK.CHF.A': 'CHF - Döviz Alış',    # Günlük, format: 01-01-2024
    'TP.DK.JPY.A': 'JPY - Döviz Alış',    # Günlük, format: 01-01-2024
}
```

### YP Mevduat / Dolarizasyon / DTH
```python
YP_MEVDUAT_SERILERI = {
    # Haftalık seriler (format: 07-01-2024, birim: Bin TL)
    'TP.YPMEVD.M01': 'A. Toplam YP Mevduatlar',
    'TP.YPMEVD.M03': 'A.II. Bankalardaki Toplam YP Mevduatlar',
    'TP.YPMEVD.M05': 'A.II.A.1. Yurtiçinde Yerleşikler',
    'TP.YPMEVD.M06': 'A.II.A.2. Yurtiçinde Yerleşik Bankalar',
    'TP.YPMEVD.M07': 'A.II.A.3. Yurtdışında Yerleşikler',
    'TP.YPMEVD.M131': 'B. Bankalardaki Toplam YP Mevduatlar (Milyon USD)',
    
    # Haftalık (Milyon USD cinsinden)
    'TP.HPBITABLO4.1': 'Toplam YP Mevduat (Milyon USD)',
    'TP.HPBITABLO4.2': 'A. Yurt İçi Yerleşikler (Milyon USD)',
    'TP.HPBITABLO4.3': '1. Gerçek Kişiler (Milyon USD)',
    'TP.HPBITABLO4.8': '2. Tüzel Kişiler (Milyon USD)',
}
# NOT: TP.YPMEVD.M01 Bin TL cinsinden, Milyar TL için /1e9 yap
```

### TL ve DTH Vadelerine Göre (Zorunlu Karşılık)
```python
TLDTH_SERILERI = {
    # Haftalık seriler (format: 07-01-2024, birim: Bin TL)
    'TP.TLDTHVADE.KB1': 'Türk Lirası Vadesiz',
    'TP.TLDTHVADE.KB2': 'Türk Lirası 1 Aya Kadar Vadeli',
    'TP.TLDTHVADE.KB3': 'Türk Lirası 3 Aya Kadar Vadeli',
    'TP.TLDTHVADE.KB6': 'Türk Lirası Toplam',
    'TP.TLDTHVADE.KB7': 'DTH Vadesiz',
    'TP.TLDTHVADE.KB12': 'DTH Toplam',
    'TP.TLDTHVADE.KB18': 'Toplam Mevduat',
}
```

### KKM (Kur Korumalı Mevduat)
```python
KKM_SERILERI = {
    # Aylık seriler
    'TP.KKM.K1': 'DDKKM Toplam (Milyar USD Karşılığı)',
    'TP.KKM.K2': 'DDKKM Gerçek Kişiler (Milyar USD Karşılığı)',
    'TP.KKM.K3': 'DDKKM Tüzel Kişiler (Milyar USD Karşılığı)',
    'TP.KKM.K4': 'TL KKM Toplam (Milyar TL)',
}
```

### Faiz / Politika Faizi / Merkez Bankası Faizi
```python
FAIZ_SERILERI = {
    'TP.PF.FF.GUN': 'TCMB Politika Faizi (Günlük)',
    'TP.TRY.MT01': 'Mevduat Faizi - 1 Aya Kadar',
    'TP.TRY.MT03': 'Mevduat Faizi - 3 Aya Kadar',
    'TP.TRY.MT06': 'Mevduat Faizi - 6 Aya Kadar',
    'TP.TRY.MT12': 'Mevduat Faizi - 1 Yıla Kadar',
    'TP.TRY.KT.TUKETICI': 'Tüketici Kredisi Faizi',
    'TP.TRY.KT.KONUT': 'Konut Kredisi Faizi',
    'TP.TRY.KT.TASIT': 'Taşıt Kredisi Faizi',
}
```

### Cari Denge / İhracat / İthalat / Dış Ticaret
```python
CARI_DENGE_SERILERI = {
    'TP.ODEMELER.CARIISLEM': 'Cari İşlemler Dengesi',
    'TP.ODEMELER.IHRACAT': 'İhracat (FOB)',
    'TP.ODEMELER.ITHALAT': 'İthalat (CIF)',
    'TP.DISTICARET.I.1': 'Dış Ticaret - İhracat',
    'TP.DISTICARET.I.2': 'Dış Ticaret - İthalat',
    'TP.DISTICARET.I.3': 'Dış Ticaret Dengesi',
}
```

### GSYH / Büyüme / Milli Gelir
```python
GSYH_SERILERI = {
    'TP.GSYIH01.N.Q': 'GSYH - Cari Fiyatlarla (Çeyreklik)',
    'TP.GSYIH02.N.Q': 'GSYH - Zincirlenmiş Hacim (Çeyreklik)',
    'TP.GSYIH03.N.Q': 'GSYH - Büyüme Oranı (%)',
    'TP.GSYIH01.N.A': 'GSYH - Cari Fiyatlarla (Yıllık)',
    'TP.UR.S06': 'GSYH Deflatörü',
}
```

### İşsizlik / İstihdam
```python
ISSIZLIK_SERILERI = {
    'TP.UR.U01': 'İşsizlik Oranı - Genel (%)',
    'TP.UR.U02': 'İşsizlik Oranı - Erkek (%)',
    'TP.UR.U03': 'İşsizlik Oranı - Kadın (%)',
    'TP.UR.U04': 'Genç İşsizlik Oranı (15-24) (%)',
    'TP.UR.U05': 'Tarım Dışı İşsizlik Oranı (%)',
    'TP.UR.I01': 'İstihdam Oranı (%)',
    'TP.UR.I02': 'İşgücüne Katılım Oranı (%)',
}
```

### Para Arzı / M1 / M2 / M3
```python
PARA_ARZI_SERILERI = {
    'TP.PR.ARZ01': 'M1 - Dar Tanımlı Para Arzı',
    'TP.PR.ARZ02': 'M2 - Geniş Tanımlı Para Arzı',
    'TP.PR.ARZ03': 'M3 - En Geniş Para Arzı',
    'TP.PR.ARZ01.YD': 'M1 - Yıllık Değişim (%)',
    'TP.PR.ARZ02.YD': 'M2 - Yıllık Değişim (%)',
}
```

### Rezerv / Döviz Rezervi
```python
REZERV_SERILERI = {
    'TP.RZV.B.TOPLAM': 'TCMB Brüt Döviz Rezervi',
    'TP.RZV.N.TOPLAM': 'TCMB Net Döviz Rezervi',
    'TP.RZV.ALTIN': 'TCMB Altın Rezervi',
}
```

## VERİ GRUBU KODLARI (Seri Keşfi İçin)

```python
VERI_GRUPLARI = {
    # Fiyatlar
    'bie_tukfiy4': 'TÜFE (2003=100)',                    # Aylık
    'bie_tufe1yi': 'ÜFE (2003=100)',                     # Aylık
    
    # Kurlar
    'bie_dkdovytl': 'Döviz Kurları',                     # Günlük
    
    # Mevduat ve Para
    'bie_ypmevd': 'YP Mevduatlar',                       # Haftalık, Bin TL
    'bie_hpbitablo4': 'YP Mevduat (Milyon USD)',         # Haftalık
    'bie_TLDTHVADE': 'TL ve DTH Vadelerine Göre',       # Haftalık, Bin TL
    'bie_kkm': 'Kur Korumalı Mevduat',                   # Aylık
    'bie_mevduat': 'Mevduatlar (Arşiv)',                 # Aylık
    
    # Faiz
    'bie_polfaiz': 'TCMB Politika Faizi',               # Günlük
    'bie_mevfaiz': 'Mevduat Faiz Oranları',             # Haftalık
    'bie_krefaiz': 'Kredi Faiz Oranları',               # Haftalık
    
    # Diğer
    'bie_pararz': 'Para Arzı',                          # Haftalık
    'bie_rezerv': 'TCMB Rezervleri',                    # Haftalık
    'bie_gsyih': 'GSYH',                                # Çeyreklik
    'bie_isgucu': 'İşgücü İstatistikleri',              # Aylık
    'bie_odedenisi': 'Ödemeler Dengesi',                # Aylık
    'bie_disticaret': 'Dış Ticaret İstatistikleri',     # Aylık
}
```

## TARİH FORMATI REFERANSI

| Frekans | Çıktı Formatı | Örnek | Parse Yöntemi |
|---------|---------------|-------|---------------|
| Aylık | `YYYY-M` | `2024-1`, `2024-12` | `pd.to_datetime(df['Tarih'], format='%Y-%m')` |
| Haftalık | `DD-MM-YYYY` | `07-01-2024` | `pd.to_datetime(df['Tarih'], format='%d-%m-%Y')` |
| Günlük | `DD-MM-YYYY` | `01-01-2024` | `pd.to_datetime(df['Tarih'], format='%d-%m-%Y')` |
| Çeyreklik | `YYYY-Q` | `2024-1` | Özel parse gerekir |

### Otomatik Tarih Parse Fonksiyonu
```python
def parse_evds_tarih(df):
    """EVDS tarih formatını otomatik algıla ve parse et."""
    tarih_str = str(df['Tarih'].iloc[0])
    
    if '-' in tarih_str:
        parcalar = tarih_str.split('-')
        if len(parcalar[0]) == 4:
            # Aylık: 2024-1 veya 2024-12
            df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m')
        else:
            # Günlük/Haftalık: 07-01-2024
            df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
    
    return df.set_index('Tarih').sort_index()
```

## BİRİM DÖNÜŞÜMLERİ

| Seri Grubu | Ham Birim | Dönüşüm |
|------------|-----------|---------|
| `TP.YPMEVD.*` | Bin TL | Milyar TL: `/1e9` |
| `TP.TLDTHVADE.*` | Bin TL | Milyar TL: `/1e9` |
| `TP.HPBITABLO4.*` | Milyon USD | Milyar USD: `/1e3` |
| `TP.KKM.*` | Milyar (USD/TL) | Doğrudan kullan |

## FREKANS DÖNÜŞÜMLERİ

Farklı frekanstaki verileri karşılaştırmak için:

```python
# Haftalık → Aylık (ay başı)
aylik = haftalik_df.resample('MS').mean()

# Günlük → Aylık
aylik = gunluk_df.resample('MS').mean()

# Aylık verinin indeksini ay başına ayarla
aylik_df.index = aylik_df.index.to_period('M').to_timestamp()
```

## AKILLI ARAMA FONKSİYONU

```python
def seri_ara(anahtar_kelime: str) -> dict:
    """
    Kullanıcının girdiği Türkçe anahtar kelimeye göre ilgili serileri döndürür.
    """
    anahtar_kelime = anahtar_kelime.lower()
    
    eslesmeler = {
        'enflasyon': ENFLASYON_SERILERI,
        'tüfe': ENFLASYON_SERILERI,
        'üfe': ENFLASYON_SERILERI,
        'fiyat': ENFLASYON_SERILERI,
        'döviz': DOVIZ_SERILERI,
        'kur': DOVIZ_SERILERI,
        'dolar': {'TP.DK.USD.A': 'USD/TRY'},
        'euro': {'TP.DK.EUR.A': 'EUR/TRY'},
        'usd': DOVIZ_SERILERI,
        'eur': DOVIZ_SERILERI,
        'yp mevduat': YP_MEVDUAT_SERILERI,
        'dolarizasyon': YP_MEVDUAT_SERILERI,
        'dth': TLDTH_SERILERI,
        'kkm': KKM_SERILERI,
        'kur korumalı': KKM_SERILERI,
        'faiz': FAIZ_SERILERI,
        'politika faizi': {'TP.PF.FF.GUN': 'TCMB Politika Faizi'},
        'mevduat faizi': FAIZ_SERILERI,
        'kredi': FAIZ_SERILERI,
        'cari': CARI_DENGE_SERILERI,
        'ihracat': CARI_DENGE_SERILERI,
        'ithalat': CARI_DENGE_SERILERI,
        'dış ticaret': CARI_DENGE_SERILERI,
        'gsyh': GSYH_SERILERI,
        'büyüme': GSYH_SERILERI,
        'milli gelir': GSYH_SERILERI,
        'işsizlik': ISSIZLIK_SERILERI,
        'istihdam': ISSIZLIK_SERILERI,
        'işgücü': ISSIZLIK_SERILERI,
        'para arzı': PARA_ARZI_SERILERI,
        'm1': PARA_ARZI_SERILERI,
        'm2': PARA_ARZI_SERILERI,
        'rezerv': REZERV_SERILERI,
        'altın': {'TP.RZV.ALTIN': 'TCMB Altın Rezervi'},
    }
    
    for kelime, seriler in eslesmeler.items():
        if kelime in anahtar_kelime:
            return seriler
    
    return {}
```

## FREKANS KODLARI

```python
FREKANSLAR = {
    1: 'Günlük',
    2: 'İşgünü',
    3: 'Haftalık',
    4: 'Ayda 2 Kez',
    5: 'Aylık',
    6: '3 Aylık (Çeyreklik)',
    7: '6 Aylık',
    8: 'Yıllık',
}
```

## FORMÜL KODLARI

```python
FORMULLER = {
    0: 'Düzey (Ham Veri)',
    1: 'Yüzde Değişim',
    2: 'Fark',
    3: 'Yıllık Yüzde Değişim',
    4: 'Yıllık Fark',
    5: 'Bir Önceki Yılın Sonuna Göre Yüzde Değişim',
    6: 'Bir Önceki Yılın Sonuna Göre Fark',
    7: 'Hareketli Ortalama',
    8: 'Hareketli Toplam',
}
```

## AGGREGATION KODLARI

```python
AGGREGATION = {
    'avg': 'Ortalama',
    'min': 'En Düşük',
    'max': 'En Yüksek',
    'first': 'İlk Değer',
    'last': 'Son Değer',
    'sum': 'Toplam',
}
```
