import curses
import sys
from typing import List, Dict, Callable, Optional


class UI:
    def __init__(self):
        self._stdscr = None
        self._altura, self._anchura = 0, 0
        self._posicion = 0
        self._usuarios: List[Dict] = []
        self._mensajes_pendientes: Dict[str, int] = {}
        self._vista_actual = "lista"
        self._chat_actual: Optional[str] = None
        self._historial_chat: Dict[str, List[tuple]] = {}
        self._input_buffer = ""
        self._callback_salir: Optional[Callable] = None
        self._callback_enviar: Optional[Callable] = None
    
    def iniciar(self):
        curses.wrapper(self._main)
    
    def _main(self, stdscr):
        self._stdscr = stdscr
        curses.curs_set(0)
        curses.noecho()
        stdscr.keypad(1)
        self._altura, self._anchura = stdscr.getmaxyx()
        
        while True:
            self._dibujar()
            key = stdscr.getch()
            if self._vista_actual == "lista":
                self._manejar_lista(key)
            elif self._vista_actual == "chat":
                self._manejar_chat(key)
            
            if key == 27:
                break
    
    def _dibujar(self):
        self._stdscr.clear()
        self._altura, self._anchura = self._stdscr.getmaxyx()
        
        if self._vista_actual == "lista":
            self._dibujar_lista()
        elif self._vista_actual == "chat":
            self._dibujar_chat()
        
        self._stdscr.refresh()
    
    def _dibujar_lista(self):
        titulo = " CHAT LAN - Presiona ESC para salir, ENTER para chatear "
        self._stdscr.addstr(0, 0, titulo[:self._anchura-1], curses.A_REVERSE)
        
        if not self._usuarios:
            msg = " Buscando usuarios en la red..."
            self._stdscr.addstr(2, 0, msg[:self._anchura-1])
            return
        
        for i, usuario in enumerate(self._usuarios):
            y = 2 + i
            if y >= self._altura - 1:
                break
            
            nick = f"  {usuario['alias']}"
            pendientes = self._mensajes_pendientes.get(usuario["ip"], 0)
            if pendientes > 0:
                nick += f" ({pendientes})"
            
            if i == self._posicion:
                self._stdscr.addstr(y, 0, nick[:self._anchura-1], curses.A_REVERSE)
            else:
                self._stdscr.addstr(y, 0, nick[:self._anchura-1])
    
    def _dibujar_chat(self):
        titulo = f" Chat con {self._chat_actual} - ESC para volver "
        self._stdscr.addstr(0, 0, titulo[:self._anchura-1], curses.A_REVERSE)
        
        historial = self._historial_chat.get(self._chat_actual, [])
        for i, (de, texto) in enumerate(historial):
            y = 2 + i
            if y >= self._altura - 2:
                break
            linea = f"{de}: {texto}"[:self._anchura-1]
            self._stdscr.addstr(y, 0, linea)
        
        y_input = self._altura - 2
        prompt = f"> {self._input_buffer}"
        self._stdscr.addstr(y_input, 0, prompt[:self._anchura-1], curses.A_UNDERLINE)
    
    def _manejar_lista(self, key):
        if key == curses.KEY_UP and self._posicion > 0:
            self._posicion -= 1
        elif key == curses.KEY_DOWN and self._posicion < len(self._usuarios) - 1:
            self._posicion += 1
        elif key == ord("\n") and self._usuarios:
            self._entrar_chat()
        elif key == 27:
            if self._callback_salir:
                self._callback_salir()
    
    def _manejar_chat(self, key):
        if key == 27:
            self._vista_actual = "lista"
            self._posicion = 0
            self._input_buffer = ""
        elif key == ord("\n"):
            if self._input_buffer.strip() and self._callback_enviar:
                self._callback_enviar(self._chat_actual, self._input_buffer)
                self._agregar_mensaje("Yo", self._input_buffer)
                self._input_buffer = ""
        elif key == 127 or key == curses.KEY_BACKSPACE:
            self._input_buffer = self._input_buffer[:-1]
        elif 32 <= key < 127:
            self._input_buffer += chr(key)
    
    def _entrar_chat(self):
        if self._usuarios and 0 <= self._posicion < len(self._usuarios):
            self._chat_actual = self._usuarios[self._posicion]["alias"]
            self._vista_actual = "chat"
            self._posicion = 0
            self._mensajes_pendientes[self._usuarios[self._posicion]["ip"]] = 0
    
    def _agregar_mensaje(self, de: str, texto: str):
        if self._chat_actual not in self._historial_chat:
            self._historial_chat[self._chat_actual] = []
        self._historial_chat[self._chat_actual].append((de, texto))
    
    def set_usuarios(self, usuarios: List[Dict]):
        self._usuarios = usuarios
    
    def set_mensaje_pendiente(self, ip: str):
        if ip not in self._mensajes_pendientes:
            self._mensajes_pendientes[ip] = 0
        self._mensajes_pendientes[ip] += 1
    
    def set_callback_salir(self, callback: Callable):
        self._callback_salir = callback
    
    def set_callback_enviar(self, callback: Callable):
        self._callback_enviar = callback
