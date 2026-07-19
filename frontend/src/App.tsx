import {
  Activity,
  AlertTriangle,
  ArrowDownToLine,
  Car,
  Check,
  Clock,
  Gauge,
  Share2,
} from "lucide-react";
import mqtt from "mqtt";
import { useCallback, useEffect, useRef, useState } from "react";

// --- Types & Interfaces ---

interface TelemetryData {
  speed_kmh: number;
  gas: number;
  brake: number;
  engine_rpm: number;
  max_rpm: number;
  steer_angle: number;
  gear: number;
  slip_angle: number[];
  car_name: string;
  track_name: string;
  lap_time: number;
  last_lap: number;
  best_lap: number;
  suspension_height: number[];
}

type ConnectionStatus = "disconnected" | "connecting" | "connected";

// --- Main Component ---

export default function App() {
  // --- State Management ---

  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const [pin, setPin] = useState<string>(() => {
    if (typeof window !== "undefined") {
      const searchParams = new URLSearchParams(window.location.search);
      const urlPin = searchParams.get("pin");
      if (urlPin && /^\d{6}$/.test(urlPin)) {
        return urlPin;
      }
    }
    return "";
  });

  const pcRef = useRef<RTCPeerConnection | null>(null);
  const watchdogRef = useRef<NodeJS.Timeout | null>(null);

  // --- Handlers & Logic ---

  const startConnection = useCallback(async () => {
    if (pin.length !== 6) return;

    setStatus("connecting");

    const brokerUrl = import.meta.env.VITE_MQTT_WS_URL;
    const topicHost = `acve/signaling/${pin}/host`;
    const topicClient = `acve/signaling/${pin}/client`;

    const mqttOptions: mqtt.IClientOptions = {};
    if (import.meta.env.VITE_MQTT_USERNAME) {
      mqttOptions.username = import.meta.env.VITE_MQTT_USERNAME;
    }
    if (import.meta.env.VITE_MQTT_PASSWORD) {
      mqttOptions.password = import.meta.env.VITE_MQTT_PASSWORD;
    }

    const client = mqtt.connect(brokerUrl, mqttOptions);

    client.on("connect", async () => {
      console.log("Connected to MQTT broker, starting WebRTC negotiation...");
      client.subscribe(topicHost);

      const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
      });
      pcRef.current = pc;

      const dc = pc.createDataChannel("telemetry", {
        ordered: false,
        maxRetransmits: 0,
      });

      // Data Channel Event Handlers
      dc.onopen = () => {
        console.log("WebRTC P2P channel opened!");
        setStatus("connected");
        setIsConnected(true);
        client.end(); // Close MQTT connection once P2P is established

        // Update URL to reflect active PIN without reloading
        const newUrl = `${window.location.pathname}?pin=${pin}`;
        window.history.replaceState({}, "", newUrl);
      };

      dc.onclose = () => {
        console.log("WebRTC channel closed.");
        if (watchdogRef.current) clearTimeout(watchdogRef.current);

        setStatus("disconnected");
        setIsConnected(false);
        setTelemetry(null);

        // Reset URL gracefully
        window.history.replaceState({}, "", window.location.pathname);
      };

      const watchDogMessage_func = () => {
        console.warn("No data received for 6s. Has the game closed?");
        setTelemetry(null);
      };

      dc.onmessage = (e: MessageEvent) => {
        try {
          const data: TelemetryData = JSON.parse(e.data);
          setTelemetry(data);

          if (watchdogRef.current) {
            clearTimeout(watchdogRef.current);
          }

          watchdogRef.current = setTimeout(watchDogMessage_func, 6000);
        } catch (error) {
          console.error("Error parsing WebRTC telemetry data:", error);
        }
      };

      // WebRTC ICE Candidate handling
      pc.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
        if (e.candidate) {
          client.publish(
            topicClient,
            JSON.stringify({
              type: "candidate",
              candidate: e.candidate.toJSON(),
            }),
          );
        }
      };

      try {
        // Create and send SDP Offer
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        client.publish(
          topicClient,
          JSON.stringify({
            type: offer.type,
            sdp: offer.sdp,
          }),
        );
      } catch (err) {
        console.error("Failed to create WebRTC offer:", err);
        setStatus("disconnected");
      }
    });

    client.on("message", async (_, message) => {
      try {
        const data = JSON.parse(message.toString());
        if (data.type === "answer" && pcRef.current) {
          await pcRef.current.setRemoteDescription(
            new RTCSessionDescription(data),
          );
        }
      } catch (err) {
        console.error("Error receiving signaling answer:", err);
      }
    });

    client.on("error", (err) => {
      console.error("MQTT connection error:", err);
      setStatus("disconnected");
    });
  }, [pin]);

  // --- Effects ---

  // Cleanup effect: Ensure RTCPeerConnection is properly closed upon unmounting
  useEffect(() => {
    return () => {
      if (pcRef.current) {
        pcRef.current.close();
      }

      if (watchdogRef.current) {
        clearTimeout(watchdogRef.current);
      }
    };
  }, []);

  // Auto-connect effect properly tracking memoized startConnection dependency.
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const urlPin = searchParams.get("pin");

    if (pin === urlPin && pin.length === 6 && status === "disconnected") {
      const connectionTimeout = setTimeout(() => {
        startConnection();
      }, 0);

      // Cleanup function to clear the timeout if the component unmounts
      return () => clearTimeout(connectionTimeout);
    }
  }, [pin, status, startConnection]);

  // --- Formatters ---

  const formatGear = (gear: number): string => {
    if (gear === -1) return "R";
    if (gear === 0) return "N";
    return gear.toString();
  };

  const formatPedal = (value: number): string => {
    return `${Math.round(value * 100)}%`;
  };

  const formatTime = (ms: number): string => {
    if (!ms || ms === 0) return "--:--.---";
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = ms % 1000;
    return `${minutes}:${seconds.toString().padStart(2, "0")}.${milliseconds
      .toString()
      .padStart(3, "0")}`;
  };

  // --- Interaction Handlers ---

  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Restrict input to digits only
    setPin(e.target.value.replace(/\D/g, ""));
  };

  const handleShareClick = async () => {
    try {
      const shareUrl = `${window.location.origin}${window.location.pathname}?pin=${pin}`;
      await navigator.clipboard.writeText(shareUrl);

      // Trigger visual feedback state
      setIsCopied(true);
      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to copy URL to clipboard:", err);
    }
  };

  // --- Render ---

  const renderContent = () => {
    if (!isConnected) {
      return (
        <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 space-y-6">
          <AlertTriangle className="w-16 h-16 opacity-50" />
          <div className="text-center space-y-2">
            <p className="text-xl">
              Waiting for connection to Assetto Corsa...
            </p>
            <p className="text-sm opacity-70">
              Enter the PIN generated by the backend
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-4 mt-4">
            <input
              type="text"
              maxLength={6}
              value={pin}
              onChange={handlePinChange}
              placeholder="123456"
              className="bg-slate-900 border border-slate-700 text-center text-2xl tracking-widest font-mono text-slate-100 rounded-lg px-6 py-3 w-48 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              onClick={startConnection}
              disabled={status === "connecting" || pin.length !== 6}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors w-full sm:w-auto"
            >
              {status === "connecting" ? "Connecting..." : "Connect"}
            </button>
          </div>
        </div>
      );
    }

    if (!telemetry) {
      return (
        <div className="flex items-center justify-center h-[60vh] text-slate-500">
          <p className="text-xl animate-pulse">Receiving P2P data...</p>
        </div>
      );
    }

    const rpmPercentage = Math.min(
      (telemetry.engine_rpm / telemetry.max_rpm) * 100,
      100,
    );

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {/* Session Info */}
        <div className="col-span-full bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Car className="text-slate-400" />
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">
                Car
              </p>
              <p className="font-semibold">{telemetry.car_name || "Unknown"}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-500 uppercase tracking-wider">
              Track
            </p>
            <p className="font-semibold capitalize">
              {telemetry.track_name || "Unknown"}
            </p>
          </div>
        </div>

        {/* Powertrain */}
        <div className="xl:col-span-2 grid grid-cols-2 gap-6 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex flex-col items-center justify-center border-r border-slate-800">
            <Gauge className="text-blue-500 w-8 h-8 mb-4 opacity-50" />
            <div className="text-5xl font-black tabular-nums tracking-tighter">
              {Math.round(telemetry.speed_kmh)}
            </div>
            <div className="text-slate-500 uppercase tracking-widest text-xs mt-2">
              km/h
            </div>
          </div>
          <div className="flex flex-col items-center justify-center">
            <div className="text-6xl font-black text-amber-400">
              {formatGear(telemetry.gear)}
            </div>
            <div className="text-slate-500 uppercase tracking-widest text-xs mt-2 font-mono">
              RPM: {Math.round(telemetry.engine_rpm)}
            </div>
            <div className="w-full bg-slate-800 h-2 mt-4 rounded-full overflow-hidden max-w-30">
              <div
                className={`h-full transition-all duration-75 ${
                  rpmPercentage > 95 ? "bg-red-500" : "bg-amber-400"
                }`}
                style={{ width: `${rpmPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Timing Deltas */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-4 text-slate-400 border-b border-slate-800 pb-2">
            <Clock className="w-4 h-4" />
            <h2 className="text-sm uppercase tracking-widest font-semibold">
              Timing
            </h2>
          </div>
          <div className="space-y-3 font-mono text-sm">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Current</span>
              <span className="text-white text-lg">
                {formatTime(telemetry.lap_time)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Last</span>
              <span className="text-slate-300">
                {formatTime(telemetry.last_lap)}
              </span>
            </div>
            <div className="flex justify-between items-center text-purple-400">
              <span>Best</span>
              <span>{formatTime(telemetry.best_lap)}</span>
            </div>
          </div>
        </div>

        {/* Pedals Input */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-center space-y-6">
          <div>
            <div className="flex justify-between text-xs mb-2 uppercase tracking-widest text-emerald-500">
              <span>Throttle</span>
              <span>{formatPedal(telemetry.gas)}</span>
            </div>
            <div className="w-full bg-slate-800 h-3 rounded-sm overflow-hidden">
              <div
                className="bg-emerald-500 h-full transition-all duration-75"
                style={{ width: formatPedal(telemetry.gas) }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs mb-2 uppercase tracking-widest text-red-500">
              <span>Brake</span>
              <span>{formatPedal(telemetry.brake)}</span>
            </div>
            <div className="w-full bg-slate-800 h-3 rounded-sm overflow-hidden">
              <div
                className="bg-red-500 h-full transition-all duration-75"
                style={{ width: formatPedal(telemetry.brake) }}
              ></div>
            </div>
          </div>
        </div>

        {/* Suspension Data */}
        <div className="col-span-full xl:col-span-2 grid grid-cols-2 gap-4 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="col-span-full flex items-center gap-2 mb-2 text-slate-400 border-b border-slate-800 pb-2">
            <ArrowDownToLine className="w-4 h-4" />
            <h2 className="text-sm uppercase tracking-widest font-semibold">
              Suspension Travel (M)
            </h2>
          </div>
          <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
            <span className="text-slate-500 text-xs">FL</span>
            <span className="font-mono text-sm">
              {telemetry.suspension_height[0].toFixed(3)}
            </span>
          </div>
          <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
            <span className="text-slate-500 text-xs">FR</span>
            <span className="font-mono text-sm">
              {telemetry.suspension_height[1].toFixed(3)}
            </span>
          </div>
          <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
            <span className="text-slate-500 text-xs">RL</span>
            <span className="font-mono text-sm">
              {telemetry.suspension_height[2].toFixed(3)}
            </span>
          </div>
          <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
            <span className="text-slate-500 text-xs">RR</span>
            <span className="font-mono text-sm">
              {telemetry.suspension_height[3].toFixed(3)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Activity className="text-blue-500 w-8 h-8" />
          <h1 className="text-2xl font-bold tracking-wider">
            VIRTUAL RACE ENGINEER
          </h1>
        </div>

        <div className="flex items-center gap-2">
          {isConnected && (
            <button
              onClick={handleShareClick}
              className={`flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg border transition-all duration-300 shadow-sm ${
                isCopied
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/50"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700 hover:border-slate-600"
              }`}
            >
              {isCopied ? (
                <Check className="w-4 h-4" />
              ) : (
                <Share2 className="w-4 h-4" />
              )}
              {isCopied ? "Copied!" : "Share Session URL"}
            </button>
          )}

          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? "bg-emerald-500 animate-pulse" : "bg-red-500"
            }`}
          ></div>
          <span className="text-sm font-medium text-slate-400 uppercase tracking-widest">
            {isConnected ? "Telemetry Active" : "Offline"}
          </span>
        </div>
      </header>

      {renderContent()}
    </div>
  );
}
