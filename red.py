import socket
import threading
import select
from protocolo import *
from typing import Dict, Callable, Optional


class ManejadorRed:
    def __init__(self, alias: str, puerto_chat: int):
        self.alias = alias
        self.puerto_chat = puerto_chat
        self.local_ip = get_local_ip()
        self.usuarios: Dict[str, dict] = {}
        self._corriendo = False
        self._callback_mensaje: Optional[Callable] = None
        self._lock = threading.Lock()
    
    def set_callback_mensaje(self, callback: Callable):
        self._callback_mensaje = callback
    
    def iniciar_broadcast(self):
        self._sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock_broadcast.bind(("", BROADCAST_PORT))
        self._sock_broadcast.setblocking(False)
        
        self._t_broadcast = threading.Thread(target=self._escuchar_broadcast, daemon=True)
        self._t_broadcast.start()
        
        self._enviar_online()
    
    def _enviar_online(self):
        msg = MensajeBroadcast(tipo="ONLINE", alias=self.alias, ip=self.local_ip, puerto=self.puerto_chat)
        data = encode_broadcast(msg)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ("<broadcast>", BROADCAST_PORT))
        sock.close()
    
    def _escuchar_broadcast(self):
        while self._corriendo:
            try:
                ready, _, _ = select.select([self._sock_broadcast], [], [], 0.5)
                if ready:
                    data, addr = self._sock_broadcast.recvfrom(4096)
                    msg = decode_broadcast(data)
                    if msg and msg.ip != self.local_ip:
                        with self._lock:
                            self.usuarios[msg.ip] = {
                                "alias": msg.alias,
                                "ip": msg.ip,
                                "puerto": msg.puerto
                            }
            except Exception:
                pass
    
    def iniciar_chat(self):
        self._sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock_chat.bind(("", self.puerto_chat))
        self._sock_chat.listen(5)
        self._sock_chat.setblocking(False)
        
        self._t_chat = threading.Thread(target=self._escuchar_chat, daemon=True)
        self._t_chat.start()
    
    def _escuchar_chat(self):
        while self._corriendo:
            try:
                ready, _, _ = select.select([self._sock_chat], [], [], 0.5)
                if ready:
                    try:
                        conn, addr = self._sock_chat.accept()
                        threading.Thread(target=self._manejar_conexion, args=(conn,), daemon=True).start()
                    except Exception:
                        pass
            except Exception:
                pass
    
    def _manejar_conexion(self, conn):
        try:
            length_data = b""
            while len(length_data) < HEADER_SIZE:
                chunk = conn.recv(HEADER_SIZE - len(length_data))
                if not chunk:
                    return
                length_data += chunk
            
            length = int.from_bytes(length_data, "big")
            data = b""
            while len(data) < length:
                chunk = conn.recv(length - len(data))
                if not chunk:
                    return
                data += chunk
            
            msg = decode_chat(data)
            if msg and self._callback_mensaje:
                self._callback_mensaje(msg)
        except Exception:
            pass
        finally:
            conn.close()
    
    def enviar_mensaje(self, ip: str, puerto: int, mensaje: str):
        msg = MensajeChat(de_alias=self.alias, de_ip=self.local_ip, mensaje=mensaje)
        data = encode_chat(msg)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, puerto))
            sock.sendall(data)
            sock.close()
            return True
        except Exception:
            return False
    
    def detener(self):
        self._corriendo = False
        if hasattr(self, "_sock_broadcast"):
            self._sock_broadcast.close()
        if hasattr(self, "_sock_chat"):
            self._sock_chat.close()
    
    def get_usuarios(self) -> Dict[str, dict]:
        with self._lock:
            return dict(self.usuarios)
