import pytest
import pandas as pd
import numpy as np
import os
from scripts.grafik import (
    cizgi_grafik,
    coklu_eksen_grafik,
    korelasyon_matrisi_grafik,
    bar_grafik,
    mevsimsellik_grafik,
    tahmin_grafik
)

@pytest.fixture
def sample_df():
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({
        "A": np.random.randn(10),
        "B": np.random.randn(10)
    }, index=dates)
    return df

def test_cizgi_grafik(sample_df, tmp_path):
    output_file = tmp_path / "test_cizgi.html"
    result = cizgi_grafik(
        df=sample_df,
        baslik="Test Çizgi Grafik",
        y_ekseni="Değerler",
        dosya_adi=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Test Çizgi Grafik" in content
    assert "Plotly.newPlot" in content

def test_coklu_eksen_grafik(sample_df, tmp_path):
    output_file = tmp_path / "test_coklu.html"
    result = coklu_eksen_grafik(
        df=sample_df,
        sol_seriler=["A"],
        sag_seriler=["B"],
        baslik="Test Çoklu Eksen",
        sol_etiket="Sol",
        sag_etiket="Sağ",
        dosya_adi=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Test Çoklu Eksen" in content
    assert "Plotly.newPlot" in content

def test_korelasyon_matrisi_grafik(sample_df, tmp_path):
    output_file = tmp_path / "test_korelasyon.html"
    result = korelasyon_matrisi_grafik(
        df=sample_df,
        baslik="Test Korelasyon",
        dosya_adi=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Test Korelasyon" in content
    assert "Plotly.newPlot" in content

def test_bar_grafik(tmp_path):
    output_file = tmp_path / "test_bar.html"
    result = bar_grafik(
        kategoriler=["Kategori 1", "Kategori 2"],
        degerler=[10.5, -5.2],
        baslik="Test Bar Grafik",
        y_ekseni="Miktar",
        dosya_adi=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Test Bar Grafik" in content
    assert "Plotly.newPlot" in content

def test_mevsimsellik_grafik(sample_df, tmp_path):
    output_file = tmp_path / "test_mevsimsellik.html"
    result = mevsimsellik_grafik(
        tarihler=sample_df.index,
        orijinal=sample_df["A"],
        trend=sample_df["A"] * 0.9,
        mevsimsel=sample_df["A"] * 0.1,
        artik=sample_df["A"] * 0.0,
        baslik="Test Mevsimsellik",
        dosya_adi=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Test Mevsimsellik" in content
    assert "Plotly.newPlot" in content

def test_tahmin_grafik(sample_df, tmp_path):
    output_file = tmp_path / "test_tahmin.html"
    tarihler = sample_df.index
    tahmin_tarihleri = pd.date_range("2023-01-11", periods=3)

    result = tahmin_grafik(
        tarihler=tarihler,
        gercek=sample_df["A"],
        tahmin=pd.Series([1.0, 2.0, 3.0]),
        tahmin_tarihleri=tahmin_tarihleri,
        alt_sinir=pd.Series([0.5, 1.5, 2.5]),
        ust_sinir=pd.Series([1.5, 2.5, 3.5]),
        baslik="Test Tahmin",
        dosya_adi=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Test Tahmin" in content
    assert "Plotly.newPlot" in content
