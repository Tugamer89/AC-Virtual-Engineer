import socket
import struct
import logging
import time

# Configurazione Logging professionale
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AC_UDP")

class ACUDPClient:
    """Gestisce esclusivamente la connessione UDP e il parsing binario con Assetto Corsa."""
    
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 9996
    
    OP_HANDSHAKE = 0
    OP_SUBSCRIBE_UPDATE = 1
    OP_DISMISS = 3

    # Formato di unpacking
    # <c 3x i 3f 6? 2x 3f 4i 5f i f 4f 4f 4f
    FMT_CAR_INFO = '<c 3x i 3f 6? 2x 3f 4i 5f i f 4f 4f 4f'
    EXPECTED_SIZE = struct.calcsize(FMT_CAR_INFO)

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(2.0)
        self.is_connected = False
        self.driver_name = ""
        self.car_name = ""
        self.track_name = ""

    def _pack_handshake(self, operation_id: int) -> bytes:
        return struct.pack('<iii', 1, 1, operation_id)

    def connect(self) -> bool:
        logger.info("Tentativo di handshake UDP...")
        try:
            self.sock.sendto(self._pack_handshake(self.OP_HANDSHAKE), (self.SERVER_IP, self.SERVER_PORT))
            
            end_time = time.time() + 2.0
            
            while time.time() < end_time:
                data, _ = self.sock.recvfrom(4096)
                
                # Controlliamo la dimensione del pacchetto
                if len(data) == 208:
                    unpacked = struct.unpack('<50s50sii50s50s', data)
                    self.car_name = unpacked[0].decode('utf-8', 'ignore').strip('\x00').split('%')[0]
                    self.driver_name = unpacked[1].decode('utf-8', 'ignore').strip('\x00').split('%')[0]
                    self.track_name = unpacked[4].decode('utf-8', 'ignore').strip('\x00').split('%')[0]
                    break
                elif len(data) == 408:
                    # Supporto futuro per Assetto Corsa Competizione
                    unpacked = struct.unpack('<100s100sii100s100s', data)
                    self.car_name = unpacked[0].decode('utf-16-le', 'ignore').strip('\x00').split('%')[0]
                    self.driver_name = unpacked[1].decode('utf-16-le', 'ignore').strip('\x00').split('%')[0]
                    self.track_name = unpacked[4].decode('utf-16-le', 'ignore').strip('\x00').split('%')[0]
                    break
                else:
                    # Scarta i pacchetti di telemetria (RTCarInfo) del tentativo precedente
                    # e continua a cercare il pacchetto di Handshake
                    continue
            else:
                logger.error("Handshake fallito: nessun dato valido ricevuto in tempo.")
                return False
            
            logger.info(f"Connesso: Pilota: {self.driver_name} | Auto: {self.car_name} | Pista: {self.track_name}")
            
            self.sock.sendto(self._pack_handshake(self.OP_SUBSCRIBE_UPDATE), (self.SERVER_IP, self.SERVER_PORT))
            self.is_connected = True
            return True
            
        except socket.timeout:
            logger.warning("Timeout UDP. AC non in pista?")
            return False
        except Exception as e:
            logger.exception(f"Errore di connessione UDP: {e}")
            return False

    def disconnect(self):
        if self.is_connected:
            self.sock.sendto(self._pack_handshake(self.OP_DISMISS), (self.SERVER_IP, self.SERVER_PORT))
            self.sock.close()
            self.is_connected = False
            logger.info("Disconnesso da AC.")

    def get_latest_data(self) -> dict:
        """Legge il pacchetto e restituisce un dizionario pulito per il frontend e la logica."""
        if not self.is_connected:
            return {}

        latest_data = None

        self.sock.setblocking(False)
        try:
            while True:
                data, _ = self.sock.recvfrom(2048)
                latest_data = data
        except BlockingIOError:
            # Errore atteso: significa che abbiamo svuotato completamente la coda!
            pass
        except Exception as e:
            pass
        finally:
            # Rimettiamo il timeout normale per evitare problemi al ciclo successivo
            self.sock.settimeout(2.0)

        try:
            if latest_data and len(latest_data) > 0 and chr(latest_data[0]) == 'a' and len(latest_data) >= self.EXPECTED_SIZE:
                unpacked = struct.unpack(self.FMT_CAR_INFO, latest_data[:self.EXPECTED_SIZE])
                
                # Mappatura pulita e tipizzata per il JSON/React
                telemetry = {
                    "speed_kmh": float(unpacked[2]),
                    "gas": float(unpacked[18]),
                    "brake": float(unpacked[19]),
                    "engine_rpm": float(unpacked[21]),
                    "steer_angle": float(unpacked[22]),
                    "gear": int(unpacked[23]) - 1, # AC invia: 0=R, 1=N, 2=1a marcia. Sottraendo 1 abbiamo -1=R, 0=N, 1=1a
                    # Estrazione array completi per grafici frontend (4 ruote)
                    "slip_angle": list(unpacked[29:33]), # [FL, FR, RL, RR]
                    "car_name": self.car_name,
                    "track_name": self.track_name
                }
                return telemetry
            return {}
            
        except socket.timeout:
            return {}
        except Exception as e:
            logger.debug(f"Errore lettura frame: {e}")
            return {}
