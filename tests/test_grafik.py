import pytest
import os
import json
import tempfile
from scripts.grafik import bar_grafik, COLORS

def test_bar_grafik_basic():
    """Test that bar_grafik creates the file correctly with basic data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        dosya_adi = os.path.join(temp_dir, "test_bar.html")
        kategoriler = ["A", "B", "C"]
        degerler = [10.5, -5.0, 0.0]
        baslik = "Test Bar Grafik"
        y_ekseni = "Test Y Ekseni"

        returned_path = bar_grafik(kategoriler, degerler, baslik, y_ekseni, dosya_adi)

        assert returned_path == dosya_adi
        assert os.path.exists(dosya_adi)

        with open(dosya_adi, 'r', encoding='utf-8') as f:
            html_content = f.read()

        assert baslik in html_content
        assert y_ekseni in html_content
        assert "Plotly.newPlot" in html_content

def test_bar_grafik_colors():
    """Test that bar_grafik assigns correct colors based on value."""
    with tempfile.TemporaryDirectory() as temp_dir:
        dosya_adi = os.path.join(temp_dir, "test_bar_colors.html")
        kategoriler = ["Pozitif", "Negatif", "Sifir"]
        degerler = [10.0, -10.0, 0.0]
        baslik = "Renk Testi"

        bar_grafik(kategoriler, degerler, baslik, dosya_adi=dosya_adi)

        with open(dosya_adi, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # extract traces from JS context
        # it looks like: var traces = [{"x": ["Pozitif", "Negatif", "Sifir"], "y": [10.0, -10.0, 0.0], "type": "bar", "marker": {"color": ["#16A085", "#E74C3C", "#16A085"]}, "hovertemplate": "<b>%{x}</b><br>De\u011fer: %{y:.2f}<extra></extra>"}];

        # Check that the expected colors are in the HTML
        accent4 = COLORS['accent4'] # positive/zero
        accent1 = COLORS['accent1'] # negative

        # Verify that these specific colors exist in the payload
        assert f'"{accent4}", "{accent1}", "{accent4}"' in html_content or f'"{accent4}", "{accent1}", "{accent4}"'.replace('"', '\\"') in html_content or f"'{accent4}', '{accent1}', '{accent4}'" in html_content or f'{json.dumps([accent4, accent1, accent4])}' in html_content


def test_bar_grafik_empty():
    """Test that bar_grafik handles empty data gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        dosya_adi = os.path.join(temp_dir, "test_bar_empty.html")
        kategoriler = []
        degerler = []
        baslik = "Bos Grafik Testi"

        returned_path = bar_grafik(kategoriler, degerler, baslik, dosya_adi=dosya_adi)

        assert returned_path == dosya_adi
        assert os.path.exists(dosya_adi)

        with open(dosya_adi, 'r', encoding='utf-8') as f:
            html_content = f.read()

        assert baslik in html_content
        assert "Plotly.newPlot" in html_content
