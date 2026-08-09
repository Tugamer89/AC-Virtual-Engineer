# Assetto Corsa Virtual Engineer

[![Backend CI](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/frontend-ci.yml)
[![CodeQL](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time telemetry analyzer and AI-powered voice-assisted race engineer for Assetto Corsa.

This application listens to Assetto Corsa's UDP telemetry stream and processes the data to calculate optimal race strategies, tire wear, and fuel deltas. Leveraging local LLMs and WebRTC, it provides real-time audio feedback alongside a modern React-based dashboard for an immersive and data-driven racing experience.

## Key Features

- **Real-Time Telemetry Processing:** High-performance UDP client reading raw data directly from Assetto Corsa with minimal latency.
- **AI Race Engineer:** Powered by local LLMs via Ollama and faster-whisper, complete with a Push-to-Talk interface for natural, bi-directional voice interactions.
- **Ultra-Low Latency Streaming:** Employs WebRTC for peer-to-peer audio and data streaming, ensuring instantaneous feedback on track.
- **Robust Messaging:** Utilizes an EMQX MQTT broker for reliable, asynchronous communication between the backend engine and frontend interface.
- **Modern Dashboard:** A sleek, responsive React 19 interface styled with Tailwind CSS v4 for visual telemetry analysis.
- **Secure & Cross-Platform:** Run the server on Windows or WSL. The backend can be compiled with PyInstaller into standalone OS-specific executables, complete with verified cryptographic dependency hashes.

## Architecture

1. **Telemetry Source:** Assetto Corsa (PC) broadcasts continuous UDP packets.
2. **Backend Engine:** A Python application ingests UDP data, processes racing logic, and orchestrates the AI voice assistant.
3. **Communication Layer:** WebRTC handles real-time audio/data streaming, while EMQX MQTT manages structured telemetry messaging.
4. **Frontend Client:** A Vite/React web application provides the interactive user dashboard, accessible from any device on your local network.

## Getting Started

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) & npm
- [Ollama](https://ollama.com/) (required for the AI Race Engineer capabilities)
- Assetto Corsa (PC Version)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Tugamer89/AC-Virtual-Engineer.git
   cd AC-Virtual-Engineer 
   ```

2. **Setup the Backend:**

    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

    _(Make sure to configure your `.env` variables for the MQTT broker and WebRTC connections as needed.)_

3. **Setup the Frontend:**

    ```bash
    cd ../frontend
    npm install
    ```

### Usage

1. **Start the Python backend server:**

    ```bash
    cd backend
    python server.py
    ```

2. **Start the Vite development server:**

    ```bash
    cd frontend
    npm run dev
    ```

3. **Launch Assetto Corsa:** Boot up the game, jump into a session, and open `http://localhost:5173` in your browser to meet your new race engineer!

## Tech Stack

- **Backend:** Python, `aiortc` (WebRTC), `aiomqtt` (MQTT), `faster-whisper`, `ollama`, `pynput`
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, `mqtt`
- **CI/CD & DevOps:** GitHub Actions, Release Please, Repository Rulesets, Dependabot, SonarCloud, CodeQL, Prettier
- **Deployment:** PyInstaller (Standalone Executables), GitHub Pages

## Contributing

Contributions are welcome! Please review our [Contributing Guidelines](CONTRIBUTING.md) and utilize our [Issue Templates](.github/ISSUE_TEMPLATE) before submitting a Pull Request. We enforce strict code quality using SonarCloud, Prettier, and standard Python linters.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
