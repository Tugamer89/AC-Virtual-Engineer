import asyncio
import websockets
import json
import logging
from ac_udp_client import ACUDPClient
from engineer_logic import VirtualEngineerLogic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainServer")

UPDATE_INTERVAL = 0.033 

async def telemetry_loop(websocket):
    """Gestisce la connessione con un client frontend specifico."""
    logger.info("Frontend connesso via WebSocket.")
    
    ac_client = ACUDPClient()
    engineer = VirtualEngineerLogic()
    
    connected = ac_client.connect()
    
    if connected:
        engineer.speak(f"Radio check. Connessione stabilita. Pronto per la telemetria di {ac_client.driver_name}.")
    
    try:
        while True:
            if ac_client.is_connected:
                telemetry_data = ac_client.get_latest_data()
                
                if telemetry_data:
                    engineer.analyze(telemetry_data)
                    await websocket.send(json.dumps(telemetry_data))
                    
            await asyncio.sleep(UPDATE_INTERVAL)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Frontend disconnesso.")
    finally:
        ac_client.disconnect()

async def main():
    logger.info("Avvio Server WebSocket su ws://0.0.0.0:8080 ...")
    async with websockets.serve(telemetry_loop, "0.0.0.0", 8080):
        await asyncio.Future()  

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server arrestato manualmente.")
