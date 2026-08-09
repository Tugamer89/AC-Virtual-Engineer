import atexit
import json
import logging
import os
import queue
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import wave
from typing import Optional

import numpy as np
import ollama
import sounddevice as sd
from engineer_logic import VirtualEngineerLogic
from faster_whisper import WhisperModel
from pynput import keyboard

logger = logging.getLogger("AIEngineer")


class OllamaManager:
    """Manages the background execution and lifecycle of the Ollama server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 11434):
        self.api_url = f"http://{host}:{port}/api/tags"
        self.process: Optional[subprocess.Popen] = None

    def is_running(self) -> bool:
        """Checks if the Ollama API is currently responding."""
        try:
            # A simple GET request to check if the server is up
            urllib.request.urlopen(self.api_url, timeout=1.0)
            return True
        except (urllib.error.URLError, ConnectionError):
            return False

    def start(self) -> None:
        """Starts the Ollama server in a headless subprocess if not already running."""
        if self.is_running():
            logger.info("Ollama server is already running. Skipping startup.")
            return

        logger.info("Starting Ollama background process...")

        kwargs = {}
        # Prevent terminal window popping up on Windows environments
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        try:
            self.process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **kwargs,
            )

            # Polling to ensure the server is ready before returning
            for _ in range(15):
                if self.is_running():
                    logger.info("Ollama background process is ready and responding.")
                    # Ensure cleanup only if we started the process
                    atexit.register(self.stop)
                    return
                time.sleep(1)

            logger.error("Failed to detect Ollama server startup within timeout.")

        except FileNotFoundError:
            logger.error(
                "Ollama executable not found. Ensure it is installed and in PATH."
            )

    def stop(self) -> None:
        """Terminates the background Ollama process gracefully."""
        if self.process:
            logger.info("Terminating managed Ollama background process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None


class RaceEngineerAI:
    """Orchestrates local Speech-to-Text and LLM logic for the race engineer."""

    def __init__(self, logic_engine: VirtualEngineerLogic):
        self.logic = logic_engine

        self.ollama_manager = OllamaManager()
        self.ollama_manager.start()

        logger.info("Initializing STT Engine (faster-whisper)...")
        try:
            # Try to load model on GPU for near-instant transcription
            self.stt = WhisperModel("base.en", device="cuda", compute_type="float16")
            logger.info("Whisper loaded successfully on GPU (CUDA).")
        except Exception as e:
            # Fallback to CPU if CUDA/GPU is unavailable
            logger.warning(f"CUDA unavailable ({e}). Falling back to CPU execution.")
            self.stt = WhisperModel("base.en", device="cpu", compute_type="int8")

        self.llm_model = "llama3.1"

        self.audio_queue: queue.Queue = queue.Queue()
        self._start_processing_thread()
        logger.info("AI Engineer background thread running.")

    def _start_processing_thread(self) -> None:
        """Starts a daemon thread to process audio without blocking WebRTC loops."""
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self) -> None:
        """Continuously polls the queue for new voice recordings."""
        while True:
            audio_path = self.audio_queue.get()
            if audio_path and os.path.exists(audio_path):
                try:
                    transcription = self._transcribe(audio_path)
                    if transcription:
                        self._analyze_and_respond(transcription)
                finally:
                    try:
                        os.remove(audio_path)
                        logger.debug(f"Temporary file deleted: {audio_path}")
                    except Exception as e:
                        logger.exception(f"Failed to delete temp audio file: {e}")

    def _transcribe(self, audio_path: str) -> str:
        """Converts saved WAV file to text using Whisper."""
        try:
            segments, _ = self.stt.transcribe(audio_path, beam_size=5, vad_filter=True, language="en")
            text = " ".join([seg.text for seg in segments]).strip()
            logger.info(f"[DRIVER VOICE]: '{text}'")
            return text
        except Exception as e:
            logger.exception(f"STT Error: {e}")
            return ""

    def _analyze_and_respond(self, text: str) -> None:
        """Extracts intent, calls telemetry tools, and generates a natural response."""
        logger.info("Evaluating intent using formatted telemetry context...")

        # Fetch the human-readable string instead of raw JSON
        telemetry_context = self.logic.get_llm_context()

        system_prompt = (
            "You are an expert motorsport race engineer guiding a driver on track. "
            "CRITICAL RULES: "
            "1. You must base your answers STRICTLY and ONLY on the 'Live Telemetry Context' provided. "
            "2. NEVER invent, guess, calculate, or hallucinate numbers, temperatures, times, or gaps. "
            "3. If the driver asks for information that is NOT present in the context, reply explicitly with: 'I don't have that data.' "
            "4. Reply directly, concisely, and realistically using racing terminology. Maximum 2 short sentences. "
            "5. Act like you are speaking over a live radio channel during a race.\n\n"
            f"Live Telemetry Context:\n{telemetry_context}"
        )

        try:
            logger.info("Generating natural vocal response via Llama...")
            final_response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            )

            reply = final_response.get("message", {}).get("content", "")
            if reply:
                self.logic.speak(reply)

        except Exception as e:
            logger.exception(f"LLM Processing Error: {e}")


class PushToTalkController:
    """Manages microphone recording bound to a keyboard key."""

    def __init__(self, ai_engine: RaceEngineerAI, key_char: str = "v"):
        self.ai_engine = ai_engine
        self.key_char = key_char
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.stream: Optional[sd.InputStream] = None

        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()
        logger.info(
            f"Push-To-Talk active. Hold '{self.key_char}' to speak to the engineer."
        )

    def on_press(self, key) -> None:
        try:
            if key.char == self.key_char and not self.is_recording:
                self.is_recording = True
                self.audio_data = []
                logger.info("Radio button pressed. Recording...")
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    callback=self._audio_callback,
                )
                self.stream.start()
        except AttributeError:
            pass

    def on_release(self, key) -> None:
        try:
            if key.char == self.key_char and self.is_recording:
                self.is_recording = False
                if self.stream:
                    self.stream.stop()
                    self.stream.close()
                logger.info("Radio button released. Processing audio...")
                self._save_and_queue()
        except AttributeError:
            pass

    def _audio_callback(self, indata, frames, time, status) -> None:
        """Appends audio chunks to buffer while recording."""
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def _save_and_queue(self) -> None:
        """Compiles audio chunks into a WAV file and passes it to the AI pipeline."""
        if not self.audio_data:
            return

        audio_np = np.concatenate(self.audio_data, axis=0)
        file_path = "temp_radio_transmission.wav"

        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            # Convert float32 to int16 PCM format
            wf.writeframes((audio_np * 32767).astype(np.int16).tobytes())

        self.ai_engine.audio_queue.put(file_path)
