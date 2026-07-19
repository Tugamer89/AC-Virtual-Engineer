import asyncio
import json
import logging
import os
import secrets
import ssl
import string
import sys
from typing import Any, Set

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


def get_resource_path(relative_path: str) -> str:
    """Resolves correct path for bundled executables (e.g., PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


env_path = get_resource_path(".env")
load_dotenv(dotenv_path=env_path)

# Suppress verbose ICE gathering logs
logging.getLogger("aioice.ice").setLevel(logging.WARNING)
logger = logging.getLogger("SignalingServer")

# Global state trackers
active_connections: Set[RTCPeerConnection] = set()
active_channels: Set[Any] = set()
background_tasks: Set[asyncio.Task] = set()


async def broadcast_telemetry(
    ac_client: ACUDPClient, engineer: VirtualEngineerLogic
) -> None:
    """Continuous loop fetching AC telemetry and broadcasting via WebRTC."""
    while True:
        if not ac_client.is_connected:
            logger.info("Attempting connection to Assetto Corsa...")
            connected = await ac_client.connect()
            if not connected:
                await asyncio.sleep(3)
                continue

        telemetry_data = ac_client.get_latest_data()

        if telemetry_data:
            _process_and_broadcast(engineer, telemetry_data)

        # 60Hz update rate approximation
        await asyncio.sleep(0.016)


def _process_and_broadcast(
    engineer: VirtualEngineerLogic, telemetry_data: dict
) -> None:
    """Passes data to the AI Engineer and pushes to all connected clients."""
    engineer.analyze(telemetry_data)
    data_str = json.dumps(telemetry_data)

    dead_channels = set()
    for channel in active_channels:
        if channel.readyState != "open":
            dead_channels.add(channel)
            continue

        try:
            channel.send(data_str)
        except Exception as e:
            logger.warning(
                f"Failed to transmit to WebRTC client. Dropping channel: {e}"
            )
            dead_channels.add(channel)

    # Cleanup broken data channels
    active_channels.difference_update(dead_channels)


async def signaling_server() -> None:
    """Handles MQTT signaling to establish peer-to-peer WebRTC connections."""
    pin = "".join(secrets.choice(string.digits) for _ in range(6))
    topic_host = f"acve/signaling/{pin}/host"
    topic_client = f"acve/signaling/{pin}/client"

    ac_client = ACUDPClient()
    engineer = VirtualEngineerLogic()

    print("=" * 60)
    print("TELEMETRY BACKEND ONLINE!")
    print(f"Dashboard: https://tugamer89.github.io/AC-Virtual-Engineer/?pin={pin}")
    print(f"AUTHENTICATION PIN: {pin}")
    print("=" * 60)

    # Dispatch background telemetry loop
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
        logger.info(f"Subscribed to MQTT signaling channel: {topic_client}")

        try:
            async for message in client.messages:
                payload_str = message.payload.decode()
                if not payload_str:
                    continue

                data = json.loads(payload_str)

                if data.get("type") == "offer":
                    await _handle_offer(data, client, topic_host)
                elif data.get("type") == "candidate":
                    await _handle_candidate(data)

        except Exception as e:
            logger.exception(f"Signaling loop interrupted: {e}")
        finally:
            logger.info("Terminating all active WebRTC sessions...")
            for pc in active_connections.copy():
                await pc.close()
            active_connections.clear()
            active_channels.clear()
            ac_client.disconnect()


async def _handle_offer(data: dict, mqtt_client: aiomqtt.Client, topic_host: str) -> None:
    """Handles incoming WebRTC SDP offers."""
    logger.info("SDP Offer received. Initiating WebRTC negotiation...")
    
    pc = RTCPeerConnection(
        configuration=RTCConfiguration(
            iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
        )
    )
    active_connections.add(pc)

    @pc.on("datachannel")
    def on_datachannel(channel):
        logger.info(f"P2P DataChannel established: {channel.label}")
        active_channels.add(channel)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange(current_pc=pc):
        state = current_pc.connectionState
        logger.info(f"WebRTC State Transition: {state}")
        if state in ["failed", "closed", "disconnected"]:
            active_connections.discard(current_pc)

    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    )
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await mqtt_client.publish(
        topic_host,
        json.dumps({
            "type": pc.localDescription.type,
            "sdp": pc.localDescription.sdp,
        }),
    )

async def _handle_candidate(data: dict) -> None:
    """Handles incoming ICE candidates."""
    candidate_info = data.get("candidate")
    if candidate_info and active_connections:
        pc = list(active_connections)[-1] 
        candidate = candidate_from_sdp(candidate_info["candidate"])
        candidate.sdpMid = candidate_info["sdpMid"]
        candidate.sdpMLineIndex = candidate_info["sdpMLineIndex"]
        await pc.addIceCandidate(candidate)


if __name__ == "__main__":
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        # Required for aioice/aiortc on Windows environments
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(signaling_server())
    except KeyboardInterrupt:
        logger.info("Process terminated by user.")
