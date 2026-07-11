import asyncio
import websockets
import json
import logging
from ac_udp_client import ACUDPClient
from engineer_logic import VirtualEngineerLogic

# Questo è il file da eseguire per avviare l'intero backend!
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainServer")

# Frequenza di invio dati al frontend (es. 0.033 sec = ~30 fps)
# Inviare dati a 60fps via WebSocket al browser è inutile e pesante. 30fps è perfetto per le dashboard.
UPDATE_INTERVAL = 0.033 

async def telemetry_loop(websocket):
    """Gestisce la connessione con un client frontend specifico."""
    logger.info("Frontend connesso via WebSocket.")
    
    ac_client = ACUDPClient()
    engineer = VirtualEngineerLogic()
    
    # Prova a connettersi ad AC in background
    connected = ac_client.connect()
    
    if connected:
        engineer.speak(f"Radio check. Connessione stabilita. Pronto per la telemetria di {ac_client.driver_name}.")
    
    try:
        while True:
            if ac_client.is_connected:
                # 1. Prendi dati fisici puliti da UDP
                telemetry_data = ac_client.get_latest_data()
                
                if telemetry_data:
                    # 2. Fai analizzare i dati al cervello per la voce
                    engineer.analyze(telemetry_data)
                    
                    # 3. Manda i dati al Frontend React in formato JSON
                    await websocket.send(json.dumps(telemetry_data))
                    
            # Pausa per mantenere il framerate richiesto senza fondere la CPU
            await asyncio.sleep(UPDATE_INTERVAL)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Frontend disconnesso.")
    finally:
        ac_client.disconnect()

async def main():
    # Avvia il server WebSocket sulla porta 8080
    logger.info("Avvio Server WebSocket su ws://0.0.0.0:8080 ...")
    async with websockets.serve(telemetry_loop, "0.0.0.0", 8080):
        # Mantiene il server attivo all'infinito
        await asyncio.Future()  

if __name__ == "__main__":
    try:
        # Avvia il loop di eventi asincroni di Python
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server arrestato manualmente.")
