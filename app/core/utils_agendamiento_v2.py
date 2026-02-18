import unicodedata
import pandas as pd


def quitar_acentos(texto: str) -> str:
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto


def normalizar_nombre(texto: str) -> str:
    texto = quitar_acentos(texto)
    texto = texto.upper().strip()
    texto = " ".join(texto.split())
    return texto


def normalizar_fecha(valor):
    if pd.isna(valor):
        return None
    return pd.to_datetime(valor, errors="coerce").date()
