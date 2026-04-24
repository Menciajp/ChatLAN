# Chat LAN por Consola

Chat de texto en tiempo real para red local (LAN) usando Python.

## Requisitos

- Python 3.8+
- Windows o Linux

## Instalación

```bash
pip install windows-curses
```

## Uso

```bash
python cliente.py
```

O desde VS Code u otro editor:

1. Abre el archivo `cliente.py`
2. Ejecutalo con el botón "Run" o presionando F5

## Cómo funciona

1. **Ingresa tu alias** al iniciar
2. La app detecta automáticamente otros usuarios en la red
3. Usa las **flechas ↑/↓** para navegar entre usuarios
4. Presiona **Enter** para abrir el chat
5. Escribe tu mensaje y **Enter** para enviar
6. Presiona **ESC** para volver al menú
7. **Ctrl+C** o **ESC** en el menú para salir (borra todo)

## Puertos

- `9998/UDP` - Descubrimiento de usuarios (broadcast)
- `9999/TCP` - Mensajería directa

## Notas

- Todos los equipos deben estar en la misma red local
- Los mensajes solo se almacenan en RAM, se borran al salir
- Compatible con Windows y Linux
