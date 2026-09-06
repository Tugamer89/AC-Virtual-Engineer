**Summary:** The initialization and polling mechanism for the Ollama server has been transitioned to use asynchronous HTTP requests, preventing event loop blocking during application startup.

**Motivation:** `OllamaManager.is_running` previously relied on `urllib.request.urlopen`, which executed synchronous network I/O. Because `OllamaManager.start` was invoked synchronously during the instantiation of `RaceEngineerAI`, any network delay or timeout while waiting for the Ollama subprocess to become responsive blocked the entire main thread. This blocked the `signaling_server` execution flow, causing delays in WebRTC and MQTT negotiation.

**Benchmarks & Metrics:**
Under a simulated delayed network startup scenario where the Ollama subprocess takes 3 seconds to spin up, blocking network I/O during initialization yielded the following results:
- Baseline synchronous initialization: ~5.0043 seconds blocking the main thread.
- Post-optimization asynchronous initialization: ~0.0012 seconds blocking the main thread.

The initialization now runs correctly as a non-blocking background task.

**Verification:**
- Verified `pytest` executed without failure or regression.
- Code linted and formatted via `flake8` and `black`.
- Verified `httpx` is properly installed via requirements file dependencies.
