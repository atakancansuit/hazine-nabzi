"""Muhasebat'ın eski .xls dosyalarını okur.

Dosyaların bir kısmında bozuk bir biçim kaydı (FORMAT) var. xlrd bu kaydı
okurken UnicodeDecodeError veriyor ve dosyanın tamamını açamıyor. Bu kayıt
yalnızca hücrelerin görünümünü (sayı biçimi) tanımlıyor, verinin kendisini
etkilemiyor. Bu yüzden hatalı kayıt atlanıyor, geri kalanı normal okunuyor.
"""
import pandas as pd
import xlrd.book
import xlrd.formatting

_original_handle_format = xlrd.formatting.handle_format


def _skip_broken_format(book, data, *args, **kwargs):
    try:
        return _original_handle_format(book, data, *args, **kwargs)
    except UnicodeDecodeError:
        pass


xlrd.formatting.handle_format = _skip_broken_format
xlrd.book.Book.handle_format = _skip_broken_format


def read_xls(source):
    """Dosyanın ilk sayfasını başlıksız, ham haliyle DataFrame olarak döndürür."""
    return pd.read_excel(source, header=None)
