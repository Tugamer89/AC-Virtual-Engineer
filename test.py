import asyncio
import websockets
import json

async def test_connection():
    # Usiamo 127.0.0.1 per puntare al server locale in esecuzione su Windows
    uri = "ws://127.0.0.1:8080"
    print(f"Tentativo di connessione al backend su {uri}...")
    
    try:
        # Si connette al server
        async with websockets.connect(uri) as websocket:
            print("Connesso con successo al WebSocket!")
            print("In attesa dei dati da Assetto Corsa (premi CTRL+C per fermare)...\n")
            
            count = 0
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                # Stampiamo solo 1 pacchetto ogni 10 per avere una lettura chiara
                if count % 10 == 0:
                    speed = data.get('speed_kmh', 0)
                    gear = data.get('gear', 0)
                    rpm = data.get('engine_rpm', 0)
                    gas = data.get('gas', 0)
                    brake = data.get('brake', 0)
                    
                    # Formattazione bella per la console
                    if gear == -1:
                        gear_str = "R"
                    elif gear == 0:
                        gear_str = "N"
                    else:
                        gear_str = str(gear)
                        
                    print(f"Velocità: {int(speed):03d} km/h | Marcia: {gear_str} | RPM: {int(rpm):04d} | Gas: {gas:.2f} | Freno: {brake:.2f}")
                
                count += 1
                
    except websockets.exceptions.ConnectionRefusedError:
        print("ERRORE: Impossibile connettersi. Assicurati di aver avviato server.py nell'altro terminale!")
    except KeyboardInterrupt:
        print("\nTest concluso.")

if __name__ == "__main__":
    asyncio.run(test_connection())
