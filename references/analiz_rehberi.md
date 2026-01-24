# EVDS Analiz Rehberi

## OTOMATİK ANALİZLER

Her veri çekiminde otomatik olarak hesapla ve göster:

### Tanımlayıcı İstatistikler

```python
def tanimlayici_istatistikler(df, seri_adi):
    """Her seri için temel istatistikleri hesaplar."""
    sonuc = {
        'seri': seri_adi,
        'baslangic': df.index.min(),
        'bitis': df.index.max(),
        'gozlem': len(df),
        'ortalama': df.mean(),
        'std': df.std(),
        'min': df.min(),
        'min_tarih': df.idxmin(),
        'max': df.max(),
        'max_tarih': df.idxmax(),
        'son_deger': df.iloc[-1],
        'eksik': df.isna().sum(),
    }
    return sonuc
```

### Trend Analizi

```python
def trend_belirle(df):
    """Son 12 gözleme göre trend yönünü belirler."""
    if len(df) < 12:
        return "Yetersiz veri"
    
    son_12 = df.tail(12)
    ilk_6_ort = son_12.head(6).mean()
    son_6_ort = son_12.tail(6).mean()
    
    degisim = (son_6_ort - ilk_6_ort) / ilk_6_ort * 100
    
    if degisim > 5:
        return "↗ Yükseliş eğiliminde"
    elif degisim < -5:
        return "↘ Düşüş eğiliminde"
    else:
        return "→ Yatay seyir"
```

## REGRESYON ANALİZLERİ

### 1. OLS (En Küçük Kareler) Regresyonu

Kullanıcı bağımlı ve bağımsız değişkenleri seçtikten sonra:

```python
import statsmodels.api as sm

def ols_regresyon(y, X, seri_adlari):
    """
    OLS regresyon analizi yapar.
    
    Parameters:
    -----------
    y : pd.Series - Bağımlı değişken
    X : pd.DataFrame - Bağımsız değişken(ler)
    seri_adlari : dict - Seri kod → isim eşleştirmesi
    
    Returns:
    --------
    dict - Model sonuçları
    """
    # Sabit ekle
    X = sm.add_constant(X)
    
    # Modeli tahmin et
    model = sm.OLS(y, X).fit()
    
    sonuc = {
        'r_kare': model.rsquared,
        'duzeltilmis_r_kare': model.rsquared_adj,
        'f_istatistigi': model.fvalue,
        'f_p_degeri': model.f_pvalue,
        'katsayilar': model.params.to_dict(),
        'p_degerleri': model.pvalues.to_dict(),
        'standart_hatalar': model.bse.to_dict(),
        'guven_araliklari': model.conf_int().to_dict(),
        'durbin_watson': sm.stats.stattools.durbin_watson(model.resid),
        'gozlem_sayisi': int(model.nobs),
        'ozet': model.summary().as_text()
    }
    return sonuc
```

**Kullanıcıya gösterilecek çıktı formatı:**
```
📈 OLS Regresyon Sonuçları
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bağımlı Değişken: TÜFE
Bağımsız Değişken(ler): Politika Faizi, USD/TRY

Model Uyumu:
  R²: 0.847
  Düzeltilmiş R²: 0.842
  F-istatistiği: 156.3 (p < 0.001)

Katsayılar:
  Sabit: 12.45*** (p=0.000)
  Politika Faizi: 0.82*** (p=0.000)
  USD/TRY: 2.34*** (p=0.002)

Diagnostik:
  Durbin-Watson: 1.87 (otokorelasyon yok)
  Gözlem: 60

*** p<0.01, ** p<0.05, * p<0.10
```

### 2. ARIMA (Otoregresif Bütünleşik Hareketli Ortalama)

```python
from pmdarima import auto_arima

def arima_analizi(y, seri_adi, tahmin_donemi=12):
    """
    Otomatik ARIMA model seçimi ve tahmin.
    
    Parameters:
    -----------
    y : pd.Series - Zaman serisi
    seri_adi : str - Seri adı
    tahmin_donemi : int - Kaç dönem ileri tahmin
    """
    # Otomatik order seçimi
    model = auto_arima(
        y,
        start_p=0, start_q=0,
        max_p=5, max_q=5,
        seasonal=True,
        m=12,  # Aylık veri için
        start_P=0, start_Q=0,
        max_P=2, max_Q=2,
        d=None,  # Otomatik fark belirleme
        D=None,
        trace=False,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True,
        information_criterion='aic'
    )
    
    # Tahmin
    tahmin, guven_araligi = model.predict(
        n_periods=tahmin_donemi,
        return_conf_int=True,
        alpha=0.05
    )
    
    sonuc = {
        'order': model.order,
        'seasonal_order': model.seasonal_order,
        'aic': model.aic(),
        'bic': model.bic(),
        'tahmin': tahmin,
        'guven_araligi_alt': guven_araligi[:, 0],
        'guven_araligi_ust': guven_araligi[:, 1],
        'ozet': model.summary().as_text()
    }
    return sonuc
```

**Kullanıcıya gösterilecek çıktı:**
```
📊 ARIMA Model Sonuçları
━━━━━━━━━━━━━━━━━━━━━━━━
Seri: TÜFE Yıllık Değişim

Model: ARIMA(2,1,1)(1,0,1)[12]

Model Uyumu:
  AIC: 234.5
  BIC: 248.3

12 Aylık Tahmin:
  2025-01: 42.3% [38.1 - 46.5]
  2025-02: 40.8% [35.2 - 46.4]
  ...
```

### 3. VAR (Vektör Otoregresyon)

Çoklu zaman serisi analizi için:

```python
from statsmodels.tsa.api import VAR

def var_analizi(df, degiskenler, max_lag=12):
    """
    VAR modeli tahmin eder.
    
    Parameters:
    -----------
    df : pd.DataFrame - Çoklu zaman serisi
    degiskenler : list - Değişken isimleri
    max_lag : int - Maksimum gecikme
    """
    # Model
    model = VAR(df[degiskenler])
    
    # Optimal lag seçimi
    lag_secimi = model.select_order(maxlags=max_lag)
    optimal_lag = lag_secimi.aic
    
    # Model tahmin
    sonuclar = model.fit(optimal_lag)
    
    # Granger nedensellik
    granger = {}
    for hedef in degiskenler:
        for kaynak in degiskenler:
            if hedef != kaynak:
                test = sonuclar.test_causality(hedef, [kaynak], kind='f')
                granger[f"{kaynak} → {hedef}"] = {
                    'f_stat': test.test_statistic,
                    'p_value': test.pvalue,
                    'sonuc': "Nedensellik VAR" if test.pvalue < 0.05 else "Nedensellik YOK"
                }
    
    return {
        'optimal_lag': optimal_lag,
        'lag_kriterleri': lag_secimi.summary().as_text(),
        'granger': granger,
        'ozet': sonuclar.summary().as_text()
    }
```

**Çıktı formatı:**
```
🔄 VAR Model Sonuçları
━━━━━━━━━━━━━━━━━━━━━━
Değişkenler: TÜFE, Politika Faizi, USD/TRY
Optimal Gecikme: 3

Granger Nedensellik Testleri:
  Politika Faizi → TÜFE: ✓ Nedensellik VAR (p=0.003)
  USD/TRY → TÜFE: ✓ Nedensellik VAR (p=0.018)
  TÜFE → Politika Faizi: ✗ Nedensellik YOK (p=0.234)
  ...
```

## MEVSİMSELLİK ANALİZİ

```python
from statsmodels.tsa.seasonal import STL

def mevsimsellik_analizi(y, seri_adi, periyot=12):
    """
    STL decomposition ile mevsimsellik analizi.
    """
    stl = STL(y, period=periyot, robust=True)
    sonuc = stl.fit()
    
    return {
        'trend': sonuc.trend,
        'mevsimsel': sonuc.seasonal,
        'artik': sonuc.resid,
        'mevsimsel_guc': sonuc.seasonal.std() / y.std(),
        'trend_guc': sonuc.trend.std() / y.std()
    }
```

## KORELASYON ANALİZİ

Çoklu seri seçildiğinde otomatik hesapla:

```python
def korelasyon_matrisi(df, metot='pearson'):
    """
    Korelasyon matrisi hesaplar.
    
    metot: 'pearson', 'spearman', 'kendall'
    """
    return df.corr(method=metot)
```

**Yorum kuralları:**
- |r| > 0.8: Çok güçlü ilişki
- |r| > 0.6: Güçlü ilişki
- |r| > 0.4: Orta düzey ilişki
- |r| > 0.2: Zayıf ilişki
- |r| < 0.2: İhmal edilebilir ilişki

## ANALİZ ÖNERİ MANTIĞI

Kullanıcı genel "analiz yap" dediğinde:

1. **Tek seri + zaman boyutu**: ARIMA öner
2. **İki seri**: Korelasyon + OLS öner
3. **Üç+ seri**: VAR + Granger öner
4. **Mevsimsel veri**: STL decomposition öner
5. **Bağımlı/bağımsız belirtilmiş**: OLS uygula

## RAPORLAMA ŞABLONU

```python
RAPOR_SABLONU = """
# {seri_adi} Analiz Raporu
Oluşturma Tarihi: {tarih}

## 1. Veri Özeti
{tanimlayici_istatistikler}

## 2. Trend Analizi
{trend_analizi}

## 3. Görselleştirme
[İnteraktif grafik]

## 4. İleri Analiz
{ileri_analiz}

## 5. Sonuç ve Değerlendirme
{sonuc}

---
Veri Kaynağı: TCMB EVDS
"""
```
