import asyncio
import json
import logging
import os
import secrets
import ssl
import string
import sys
import time

import aiomqtt
from ac_udp_client import ACUDPClient
from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.sdp import candidate_from_sdp
from dotenv import load_dotenv
from engineer_logic import VirtualEngineerLogic


def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


env_path = get_resource_path(".env")
load_dotenv(dotenv_path=env_path)

logging.getLogger("aioice.ice").setLevel(logging.WARNING)

active_connections: set[RTCPeerConnection] = set()
active_channels: set[str] = set()
background_tasks = set()  # type: ignore[var-annotated]


async def broadcast_telemetry(ac_client, engineer):
    last_packet_time = time.time()

    while True:
        if not ac_client.is_connected:
            print("Attempting to connect to Assetto Corsa...")
            connected = await ac_client.connect()
            if not connected:
                await asyncio.sleep(3)
                continue
            last_packet_time = time.time()

        telemetry_data = ac_client.get_latest_data()

        if telemetry_data:
            _process_and_broadcast(engineer, telemetry_data)
            last_packet_time = time.time()
        elif time.time() - last_packet_time > 3.0 and ac_client.is_connected:
            print("UDP timeout: Game likely closed. Forcing handshake renewal...")
            ac_client.disconnect()

        await asyncio.sleep(0.016)


def _process_and_broadcast(engineer, telemetry_data):
    engineer.analyze(telemetry_data)
    data_str = json.dumps(telemetry_data)
    channels = list(active_channels)

    for channel in channels:
        if channel.readyState != "open":
            active_channels.discard(channel)
            continue

        try:
            channel.send(data_str)
        except Exception as e:
            print(f"Error sending to a client, removing it: {e}")
            active_channels.discard(channel)


async def signaling_server():
    pin = "".join(secrets.choice(string.digits) for _ in range(6))
    topic_host = f"acve/signaling/{pin}/host"
    topic_client = f"acve/signaling/{pin}/client"

    ac_client = ACUDPClient()
    engineer = VirtualEngineerLogic()

    print("=" * 60)
    print("TELEMETRY SERVER STARTED SUCCESSFULLY!")
    print(f"OPEN: https://tugamer89.github.io/AC-Virtual-Engineer/?pin={pin}")
    print("=" * 60)

    task = asyncio.create_task(broadcast_telemetry(ac_client, engineer))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    tls_context = ssl.create_default_context()
    mqtt_host = os.environ.get("MQTT_HOST")
    mqtt_user = os.environ.get("MQTT_USERNAME")
    mqtt_pass = os.environ.get("MQTT_PASSWORD")

    async with aiomqtt.Client(
        hostname=mqtt_host,
        port=8883,
        tls_context=tls_context,
        username=mqtt_user,
        password=mqtt_pass,
    ) as client:
        await client.subscribe(topic_client)

        try:
            async for message in client.messages:
                data = json.loads(message.payload.decode())

                if data.get("type") == "offer":
                    print(
                        "Connection request received! WebRTC negotiation in progress..."
                    )
                    pc = RTCPeerConnection(
                        configuration=RTCConfiguration(
                            iceServers=[
                                RTCIceServer(urls=["stun:stun.l.google.com:19302"])
                            ]
                        )
                    )
                    active_connections.add(pc)

                    @pc.on("datachannel")
                    def on_datachannel(channel):
                        print(
                            "P2P connection established! "
                            f"Telemetry streaming on channel: {channel.label}"
                        )
                        active_channels.add(channel)

                    @pc.on("connectionstatechange")
                    async def on_connectionstatechange(current_pc=pc):
                        if current_pc.connectionState in ["failed", "closed"]:
                            print("A client has disconnected.")
                            active_connections.discard(current_pc)

                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                    )
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)

                    await client.publish(
                        topic_host,
                        json.dumps(
                            {
                                "type": pc.localDescription.type,
                                "sdp": pc.localDescription.sdp,
                            }
                        ),
                    )

                elif data.get("type") == "candidate":
                    candidate_info = data["candidate"]
                    if candidate_info:
                        candidate = candidate_from_sdp(candidate_info["candidate"])
                        candidate.sdpMid = candidate_info["sdpMid"]
                        candidate.sdpMLineIndex = candidate_info["sdpMLineIndex"]
                        await pc.addIceCandidate(candidate)
        finally:
            print("\Closing all active WebRTC connections...")
            conn_list = list(active_connections)
            for pc in conn_list:
                await pc.close()
            active_connections.clear()
            active_channels.clear()


if __name__ == "__main__":
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]

    try:
        asyncio.run(signaling_server())
    except KeyboardInterrupt:
        print("\nShutting down the server.")
