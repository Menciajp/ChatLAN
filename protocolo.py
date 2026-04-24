import json
import socket
from dataclasses import dataclass
from typing import Optional


BROADCAST_PORT = 9998
CHAT_PORT = 9999
HEADER_SIZE = 4


@dataclass
class MensajeBroadcast:
    tipo: str
    alias: str
    ip: str
    puerto: int


@dataclass
class MensajeChat:
    de_alias: str
    de_ip: str
    mensaje: str


def encode_broadcast(msg: MensajeBroadcast) -> bytes:
    data = json.dumps({
        "tipo": msg.tipo,
        "alias": msg.alias,
        "ip": msg.ip,
        "puerto": msg.puerto
    })
    return data.encode("utf-8")


def decode_broadcast(data: bytes) -> Optional[MensajeBroadcast]:
    try:
        d = json.loads(data.decode("utf-8"))
        return MensajeBroadcast(
            tipo=d["tipo"],
            alias=d["alias"],
            ip=d["ip"],
            puerto=d["puerto"]
        )
    except Exception:
        return None


def encode_chat(msg: MensajeChat) -> bytes:
    data = json.dumps({
        "de_alias": msg.de_alias,
        "de_ip": msg.de_ip,
        "mensaje": msg.mensaje
    })
    length = len(data).to_bytes(HEADER_SIZE, "big")
    return length + data.encode("utf-8")


def decode_chat(data: bytes) -> Optional[MensajeChat]:
    try:
        d = json.loads(data.decode("utf-8"))
        return MensajeChat(
            de_alias=d["de_alias"],
            de_ip=d["de_ip"],
            mensaje=d["mensaje"]
        )
    except Exception:
        return None


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip
