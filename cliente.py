import sys
import threading
import time
from protocolo import CHAT_PORT, get_local_ip
from red import ManejadorRed
from ui import UI


class ClienteChat:
    def __init__(self):
        self.ui = UI()
        self.red = None
        self.alias = ""
        self._corriendo = False
    
    def iniciar(self):
        print("=== CHAT LAN ===")
        print()
        
        self.alias = input("Ingresa tu alias: ").strip()
        if not self.alias:
            print("Alias no puede estar vacío.")
            return
        
        ip_local = get_local_ip()
        print(f"Tu IP local: {ip_local}")
        print(f"Usando puerto: {CHAT_PORT}")
        
        self.red = ManejadorRed(self.alias, CHAT_PORT)
        self.red.set_callback_mensaje(self._on_mensaje_recibido)
        
        try:
            self.red.iniciar_broadcast()
            self.red.iniciar_chat()
            self._corriendo = True
            print("Buscando usuarios en la red...")
        except Exception as e:
            print(f"Error al iniciar red: {e}")
            return
        
        self.ui.set_callback_salir(self._salir)
        self.ui.set_callback_enviar(self._enviar_mensaje)
        
        self._hilo_actualizador = threading.Thread(target=self._actualizar_usuarios, daemon=True)
        self._hilo_actualizador.start()
        
        try:
            self.ui.iniciar()
        except KeyboardInterrupt:
            pass
        finally:
            self._salir()
    
    def _actualizar_usuarios(self):
        while self._corriendo:
            usuarios = list(self.red.get_usuarios().values())
            self.ui.set_usuarios(usuarios)
            time.sleep(1)
    
    def _on_mensaje_recibido(self, msg):
        self.ui.set_mensaje_pendiente(msg.de_ip)
        print(f"\nNuevo mensaje de {msg.de_alias}: {msg.mensaje[:50]}...")
    
    def _enviar_mensaje(self, alias: str, texto: str):
        usuarios = self.red.get_usuarios()
        for ip, datos in usuarios.items():
            if datos["alias"] == alias:
                ok = self.red.enviar_mensaje(ip, datos["puerto"], texto)
                if not ok:
                    print(f"Error al enviar a {alias}")
                return
    
    def _salir(self):
        if self._corriendo:
            self._corriendo = False
            if self.red:
                self.red.detener()
        sys.exit(0)


if __name__ == "__main__":
    ClienteChat().iniciar()
