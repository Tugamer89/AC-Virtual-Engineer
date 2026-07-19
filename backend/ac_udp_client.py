import socket
import struct
import logging
import time
import asyncio

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AC_UDP")


class ACUDPClient:
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 9996

    OP_HANDSHAKE = 0
    OP_SUBSCRIBE_UPDATE = 1
    OP_DISMISS = 3

    FMT_CAR_INFO = "<c 3x i 3f 6? 2x 3f 4i 5f i f 4f 4f 4f"
    EXPECTED_SIZE = struct.calcsize(FMT_CAR_INFO)

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.is_connected = False
        self.driver_name = ""
        self.car_name = ""
        self.track_name = ""

    def _pack_handshake(self, operation_id: int) -> bytes:
        return struct.pack("<iii", 1, 1, operation_id)

    async def connect(self) -> bool:
        logger.info("UDP handshake attempt...")
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

                    if len(data) == 208:
                        unpacked = struct.unpack("<50s50sii50s50s", data)
                        self.car_name = (
                            unpacked[0]
                            .decode("utf-8", "ignore")
                            .strip("\x00")
                            .split("%")[0]
                        )
                        self.driver_name = (
                            unpacked[1]
                            .decode("utf-8", "ignore")
                            .strip("\x00")
                            .split("%")[0]
                        )
                        self.track_name = (
                            unpacked[4]
                            .decode("utf-8", "ignore")
                            .strip("\x00")
                            .split("%")[0]
                        )
                        break
                    elif len(data) == 408:
                        unpacked = struct.unpack("<100s100sii100s100s", data)
                        self.car_name = (
                            unpacked[0]
                            .decode("utf-16-le", "ignore")
                            .strip("\x00")
                            .split("%")[0]
                        )
                        self.driver_name = (
                            unpacked[1]
                            .decode("utf-16-le", "ignore")
                            .strip("\x00")
                            .split("%")[0]
                        )
                        self.track_name = (
                            unpacked[4]
                            .decode("utf-16-le", "ignore")
                            .strip("\x00")
                            .split("%")[0]
                        )
                        break
                except asyncio.TimeoutError:
                    continue

            else:
                logger.error("Handshake failed: no valid data received in time.")
                return False

            logger.info(
                f"Connected: Driver: {self.driver_name} | "
                f"Car: {self.car_name} | Track: {self.track_name}"
            )

            self.sock.sendto(
                self._pack_handshake(self.OP_SUBSCRIBE_UPDATE),
                (self.SERVER_IP, self.SERVER_PORT),
            )
            self.is_connected = True
            return True

        except Exception as e:
            logger.exception(f"UDP connection error: {e}")
            return False

    def disconnect(self):
        if self.is_connected:
            self.sock.sendto(
                self._pack_handshake(self.OP_DISMISS),
                (self.SERVER_IP, self.SERVER_PORT),
            )
            self.sock.close()
            self.is_connected = False
            logger.info("Disconnected from AC.")

    def get_latest_data(self) -> dict:
        if not self.is_connected:
            return {}

        latest_data = None
        try:
            while True:
                data, _ = self.sock.recvfrom(2048)
                latest_data = data
        except BlockingIOError:
            pass
        except Exception:
            pass

        if (
            latest_data
            and len(latest_data) > 0
            and chr(latest_data[0]) == "a"
            and len(latest_data) >= self.EXPECTED_SIZE
        ):
            unpacked = struct.unpack(
                self.FMT_CAR_INFO, latest_data[: self.EXPECTED_SIZE]
            )

            return {
                "speed_kmh": float(unpacked[2]),
                "gas": float(unpacked[18]),
                "brake": float(unpacked[19]),
                "engine_rpm": float(unpacked[21]),
                "steer_angle": float(unpacked[22]),
                "gear": int(unpacked[23]) - 1,
                "slip_angle": list(unpacked[29:33]),
                "car_name": self.car_name,
                "track_name": self.track_name,
            }
        return {}
