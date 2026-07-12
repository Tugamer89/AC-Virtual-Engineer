# Assetto Corsa Virtual Engineer

[![Backend CI](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/frontend-ci.yml)
[![CodeQL](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tugamer89/AC-Virtual-Engineer/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time telemetry analyzer and voice-assisted race engineer for Assetto Corsa.

This application listens to Assetto Corsa's UDP telemetry stream, processes the data to calculate optimal race strategies, tire wear, and fuel deltas, and provides real-time audio feedback via a TTS (Text-to-Speech) worker, paired with a sleek React-based dashboard.

## Features

- **Real-Time Telemetry:** Fast, low-latency UDP client reading directly from Assetto Corsa.
- **Voice Feedback:** Get audible updates on your pace, fuel, and track conditions.
- **Modern Dashboard:** React/Vite web interface for visual telemetry analysis.
- **Cross-Platform:** Run the server on your main Windows rig or WSL, and access the UI from any device on your local network.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ & npm
- Assetto Corsa (PC Version)

### Installation

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/Tugamer89/AC-Virtual-Engineer.git](https://github.com/Tugamer89/AC-Virtual-Engineer.git)
   cd AC-Virtual-Engineer 
   ```

2. **Setup the Backend:**

    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Setup the Frontend:**

    ```bash
    cd ../frontend
    npm install
    ```

### Usage

1. Start the Python backend server:

    ```bash
    cd backend
    python server.py
    ```

2. Start the Vite development server:

    ```bash
    cd frontend
    npm run dev
    ```

3. Boot up Assetto Corsa, jump into a session, and open `http://localhost:5173` to see your virtual engineer in action!

## Tech Stack

- **Backend:** Python (UDP Client, TTS Engine)
- **Frontend:** React, TypeScript, Vite
- **CI/CD:** GitHub Actions, Release Please, Dependabot

## Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md) and our [Issue Templates](.github/ISSUE_TEMPLATE) before submitting a PR.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
