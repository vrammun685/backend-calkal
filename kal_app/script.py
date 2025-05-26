# mi_app/script.py
import time
import threading
from datetime import datetime
from .utils import Crear_Diarios_auto, mensaje_Almuerzo, mensaje_Desayuno, mensaje_Cena

HORAS_OBJETIVO = ["08:45", "10:00", "16:00", "23:00"]
ejecutadas_hoy = set()

def run_script():
    global ejecutadas_hoy
    while True:
        print('Se ejecuta')
        ahora = datetime.now()
        hora_actual = ahora.strftime("%H:%M")

        if hora_actual in HORAS_OBJETIVO and hora_actual not in ejecutadas_hoy:
            print(f"Tarea programada para las {hora_actual}")
            ejecutadas_hoy.add(hora_actual)

            match hora_actual:
                case "08:45":
                    Crear_Diarios_auto()  # Solo esto se ejecuta si hora_actual == "00:00"
                case "10:00":
                    mensaje_Desayuno()
                case "16:00":
                    mensaje_Almuerzo()
                case "23:00":
                    print("tareaNoche")
                    mensaje_Cena()
        
        if hora_actual == "09:00":
            ejecutadas_hoy = set()

        time.sleep(60)

def start_in_background():
    thread = threading.Thread(target=run_script, daemon=True)
    thread.start()