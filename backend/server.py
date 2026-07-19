import asyncio
import json
import random
import string
import aiomqtt
import ssl
import sys
import os
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)
from aiortc.sdp import candidate_from_sdp
from ac_udp_client import ACUDPClient
from engineer_logic import VirtualEngineerLogic
from dotenv import load_dotenv
import logging


def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


env_path = get_resource_path(".env")
load_dotenv(dotenv_path=env_path)

logging.getLogger("aioice.ice").setLevel(logging.WARNING)

active_connections: set[RTCPeerConnection] = set()
active_channels: set[str] = set()

async def broadcast_telemetry(ac_client, engineer):
    connesso = await ac_client.connect()
    if not connesso:
        print("Impossibile connettersi ad Assetto Corsa. Auto in pista?")
        return

    while True:
        telemetry_data = ac_client.get_latest_data()

        if telemetry_data:
            engineer.analyze(telemetry_data)
            data_str = json.dumps(telemetry_data)

            for channel in active_channels:
                if channel.readyState == "open":
                    try:
                        channel.send(data_str)
                    except Exception as e:
                        print(f"Errore invio a un client, lo rimuovo: {e}")
                        active_channels.discard(channel)

        await asyncio.sleep(0.016)


async def signaling_server():
    pin = "".join(random.choices(string.digits, k=6))
    topic_host = f"acve/signaling/{pin}/host"
    topic_client = f"acve/signaling/{pin}/client"

    ac_client = ACUDPClient()
    engineer = VirtualEngineerLogic()

    print("=" * 60)
    print("SERVER TELEMETRIA AVVIATO CON SUCCESSO!")
    print("Vai su: https://tugamer89.github.io/AC-Virtual-Engineer")
    print(f"INSERISCI QUESTO PIN: {pin}")
    print("=" * 60)

    asyncio.create_task(broadcast_telemetry(ac_client, engineer))

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

        async for message in client.messages:
            data = json.loads(message.payload.decode())

            if data.get("type") == "offer":
                print(
                    "Richiesta di connessione ricevuta! Negoziazione WebRTC in corso..."
                )
                pc = RTCPeerConnection(
                    configuration=RTCConfiguration(
                        iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
                    )
                )
                active_connections.add(pc)

                @pc.on("datachannel")
                def on_datachannel(channel):
                    print(
                        "Connessione P2P stabilita! "
                        f"Telemetria in streaming sul canale: {channel.label}"
                    )
                    active_channels.add(channel)

                @pc.on("connectionstatechange")
                async def on_connectionstatechange():
                    if pc.connectionState in ["failed", "closed"]:
                        print("Un client si è disconnesso.")
                        active_connections.discard(pc)

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


if __name__ == "__main__":
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # type: ignore[attr-defined]

    try:
        asyncio.run(signaling_server())
    except KeyboardInterrupt:
        print("\nChiusura del server.")
