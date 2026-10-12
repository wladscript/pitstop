from django.core.exceptions import ValidationError
from .models import format_placa


def consultar_placa(placa_raw: str) -> dict:
    """
    Mock determinístico para consulta de placa de veículo,
    preparado para substituição futura por API externa (Sinesp / Carcheck).
    """
    placa = format_placa(placa_raw)
    if len(placa) < 7:
        raise ValidationError("Placa deve conter pelo menos 7 caracteres.")

    modelos = [
        "Volkswagen Gol",
        "Fiat Uno",
        "Chevrolet Onix",
        "Toyota Corolla",
        "Honda Civic",
        "Jeep Compass",
    ]
    cores = ["Prata", "Preto", "Branco", "Vermelho", "Azul"]
    categorias = ["Pequeno", "Médio", "Grande"]

    seed = sum(ord(c) for c in placa)
    return {
        "placa": placa,
        "modelo": modelos[seed % len(modelos)],
        "cor": cores[seed % len(cores)],
        "ano": 2015 + (seed % 10),
        "categoria": categorias[seed % len(categorias)],
        "fonte": "mock",
    }
