import io
import unicodedata
from decimal import Decimal
import segno
from django.conf import settings


def _crc16(payload: str) -> str:
    poly = 0x1021
    result = 0xFFFF
    for b in payload.encode("utf-8"):
        result ^= b << 8
        for _ in range(8):
            if result & 0x8000:
                result = ((result << 1) ^ poly) & 0xFFFF
            else:
                result = (result << 1) & 0xFFFF
    return format(result, "04X")


def _tlv(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"


def _sanitize(txt: str, maxlen: int) -> str:
    nkfd = unicodedata.normalize("NFKD", txt)
    ascii_txt = "".join(c for c in nkfd if not unicodedata.combining(c))
    return ascii_txt.upper()[:maxlen]


def gerar_brcode_pix(pix_key: str, nome: str, cidade: str, valor: Decimal, txid: str) -> str:
    """
    Gera string padrão BR Code estático Pix (Copia e Cola) do Banco Central com CRC16.
    """
    gui = _tlv("00", "br.gov.bcb.pix") + _tlv("01", pix_key)
    merchant_account = _tlv("26", gui)
    payload = (
        _tlv("00", "01")
        + merchant_account
        + _tlv("52", "0000")
        + _tlv("53", "986")
        + _tlv("54", f"{valor:.2f}")
        + _tlv("58", "BR")
        + _tlv("59", _sanitize(nome, 25))
        + _tlv("60", _sanitize(cidade, 15))
        + _tlv("62", _tlv("05", _sanitize(txid, 25)))
    )
    payload += "6304"
    crc = _crc16(payload)
    return payload + crc


def gerar_qrcode_svg(payload: str) -> str:
    """
    Gera o QR Code diretamente em SVG no servidor sem nenhuma dependência de API externa.
    """
    qr = segno.make(payload, error="m")
    buffer = io.BytesIO()
    qr.save(buffer, kind="svg", scale=6, dark="#ffffff", light="#0a0a0a")
    return buffer.getvalue().decode("utf-8")


def gerar_dados_pix_os(ordem):
    """
    Gera o código copia-e-cola e o SVG do QR Code para a OS.
    """
    pix_key = getattr(settings, "PIX_KEY", "pitstop@pix.com.br")
    nome = getattr(settings, "PIX_RECEIVER_NAME", "PIT STOP LAVA RAPIDO")
    cidade = getattr(settings, "PIX_RECEIVER_CITY", "SAO PAULO")
    txid = f"OS{ordem.id:04d}"

    copia_e_cola = gerar_brcode_pix(
        pix_key=pix_key,
        nome=nome,
        cidade=cidade,
        valor=ordem.valor_total,
        txid=txid,
    )
    qrcode_svg = gerar_qrcode_svg(copia_e_cola)

    return {
        "copia_e_cola": copia_e_cola,
        "qrcode_svg": qrcode_svg,
        "txid": txid,
        "valor": ordem.valor_total,
        "chave": pix_key,
        "recebedor": nome,
        "cidade": cidade,
    }
