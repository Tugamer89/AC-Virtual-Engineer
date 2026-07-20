import asyncio
import logging
import socket
import struct
import time
from typing import List, Optional, Tuple, TypedDict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AC_UDP")


class TelemetryData(TypedDict):
    speed_kmh: float
    gas: float
    brake: float
    engine_rpm: float
    max_rpm: float
    steer_angle: float
    gear: int
    slip_angle: List[float]
    car_name: str
    track_name: str
    lap_time: int
    last_lap: int
    best_lap: int
    suspension_height: List[float]


class ACUDPClient:
    """UDP Client for communicating with Assetto Corsa telemetry server."""

    SERVER_IP: str = "127.0.0.1"
    SERVER_PORT: int = 9996

    OP_HANDSHAKE: int = 0
    OP_SUBSCRIBE_UPDATE: int = 1
    OP_DISMISS: int = 3

    # Format string for AC telemetry unpacking
    FMT_CAR_INFO: str = "<c 3x i 3f 6? 2x 3f 4i 5f i f 56f f f 3f"
    EXPECTED_SIZE: int = struct.calcsize(FMT_CAR_INFO)

    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.is_connected: bool = False

        self.driver_name: str = ""
        self.car_name: str = ""
        self.track_name: str = ""
        self.max_rpm: float = 8000.0
        
        self.last_packet_time: float = 0.0

    def _pack_handshake(self, operation_id: int) -> bytes:
        """Packs the handshake request bytes."""
        return struct.pack("<iii", 1, 1, operation_id)

    async def connect(self) -> bool:
        """Asynchronously establishes the UDP handshake with Assetto Corsa."""
        logger.info("Initiating UDP handshake attempt...")
        loop = asyncio.get_running_loop()

        try:
            self.sock.sendto(
                self._pack_handshake(self.OP_HANDSHAKE),
                (self.SERVER_IP, self.SERVER_PORT),
            )

            end_time = time.time() + 2.0
            while time.time() < end_time:
                timeout_left = end_time - time.time()
                if timeout_left <= 0:
                    break

                try:
                    data = await asyncio.wait_for(
                        loop.sock_recv(self.sock, 4096), timeout=timeout_left
                    )

                    # Assetto Corsa handshake response size variations
                    if len(data) == 208:
                        unpacked_208 = struct.unpack("<50s50sii50s50s", data)
                        self.car_name = self._decode_string(unpacked_208[0], "utf-8")
                        self.driver_name = self._decode_string(unpacked_208[1], "utf-8")
                        self.track_name = self._decode_string(unpacked_208[4], "utf-8")
                        break
                    elif len(data) == 408:
                        unpacked_408 = struct.unpack("<100s100sii100s100s", data)
                        self.car_name = self._decode_string(
                            unpacked_408[0], "utf-16-le"
                        )
                        self.driver_name = self._decode_string(
                            unpacked_408[1], "utf-16-le"
                        )
                        self.track_name = self._decode_string(
                            unpacked_408[4], "utf-16-le"
                        )
                        break

                except asyncio.TimeoutError:
                    continue
                except ConnectionResetError:
                    return False

            else:
                logger.error("Handshake failed: No valid data received within timeout.")
                return False

            logger.info(
                f"Connected Successfully | Driver: {self.driver_name} | "
                f"Car: {self.car_name} | Track: {self.track_name}"
            )

            self.sock.sendto(
                self._pack_handshake(self.OP_SUBSCRIBE_UPDATE),
                (self.SERVER_IP, self.SERVER_PORT),
            )
            self.is_connected = True
            self.last_packet_time = time.time()
            return True

        except Exception as e:
            logger.exception(f"UDP connection error encountered: {e}")
            return False

    def _decode_string(self, raw_bytes: bytes, encoding: str) -> str:
        """Helper method to decode and clean AC byte strings."""
        return raw_bytes.decode(encoding, "ignore").strip("\x00").split("%")[0]

    def disconnect(self) -> None:
        """Sends a dismissal signal and closes the socket."""
        if self.is_connected:
            self.sock.sendto(
                self._pack_handshake(self.OP_DISMISS),
                (self.SERVER_IP, self.SERVER_PORT),
            )
            self.sock.close()
            self.is_connected = False
            logger.info("Successfully disconnected from Assetto Corsa.")

    def get_latest_data(self) -> Optional[TelemetryData]:
        """Retrieves and unpacks the latest telemetry payload."""
        if not self.is_connected:
            return None

        latest_data: Optional[bytes] = None
        try:
            while True:
                data, _ = self.sock.recvfrom(2048)
                latest_data = data
        except BlockingIOError:
            pass
        except Exception as e:
            logger.debug(f"Socket read error: {e}")

        if (
            latest_data
            and len(latest_data) > 0
            and chr(latest_data[0]) == "a"
            and len(latest_data) >= self.EXPECTED_SIZE
        ):
            self.last_packet_time = time.time()
            
            unpacked = struct.unpack(
                self.FMT_CAR_INFO, latest_data[: self.EXPECTED_SIZE]
            )

            current_rpm = float(unpacked[21])
            if current_rpm > self.max_rpm:
                self.max_rpm = current_rpm

            return {
                "speed_kmh": float(unpacked[2]),
                "gas": float(unpacked[18]),
                "brake": float(unpacked[19]),
                "engine_rpm": current_rpm,
                "max_rpm": self.max_rpm,
                "steer_angle": float(unpacked[22]),
                "gear": int(unpacked[23]) - 1,
                "slip_angle": list(unpacked[29:33]),
                "car_name": self.car_name,
                "track_name": self.track_name,
                "lap_time": int(unpacked[14]),
                "last_lap": int(unpacked[15]),
                "best_lap": int(unpacked[16]),
                "suspension_height": list(unpacked[77:81]),
            }
            
        if time.time() - self.last_packet_time > 3.0:
            logger.info("Session ended by user (Timeout). Ready for next session.")
            self.is_connected = False

        return None
