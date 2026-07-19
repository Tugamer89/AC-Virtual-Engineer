import { useEffect, useState, useRef } from "react";
import { Activity, Gauge, Car, AlertTriangle } from "lucide-react";
import mqtt from "mqtt";

interface TelemetryData {
  speed_kmh: number;
  gas: number;
  brake: number;
  engine_rpm: number;
  steer_angle: number;
  gear: number;
  slip_angle: number[];
  car_name: string;
  track_name: string;
}

export default function App() {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState<
    "disconnected" | "connecting" | "connected"
  >("disconnected");
  const [pin, setPin] = useState("");

  const pcRef = useRef<RTCPeerConnection | null>(null);

  const startConnection = async () => {
    if (pin.length !== 6) return;
    setStatus("connecting");

    const brokerUrl = import.meta.env.VITE_MQTT_WS_URL;
    const topicHost = `acve/signaling/${pin}/host`;
    const topicClient = `acve/signaling/${pin}/client`;

    const mqttOptions: mqtt.IClientOptions = {};
    if (import.meta.env.VITE_MQTT_USERNAME)
      mqttOptions.username = import.meta.env.VITE_MQTT_USERNAME;
    if (import.meta.env.VITE_MQTT_PASSWORD)
      mqttOptions.password = import.meta.env.VITE_MQTT_PASSWORD;

    const client = mqtt.connect(brokerUrl, mqttOptions);

    client.on("connect", async () => {
      console.log("Connesso al broker MQTT, inizio negoziazione WebRTC...");
      client.subscribe(topicHost);

      const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
      });
      pcRef.current = pc;

      const dc = pc.createDataChannel("telemetry", {
        ordered: false,
        maxRetransmits: 0,
      });

      dc.onopen = () => {
        console.log("Canale WebRTC P2P aperto!");
        setStatus("connected");
        setIsConnected(true);
        client.end();
      };

      dc.onclose = () => {
        console.log("Canale WebRTC chiuso.");
        setStatus("disconnected");
        setIsConnected(false);
        setTelemetry(null);
      };

      dc.onmessage = (e) => {
        try {
          const data: TelemetryData = JSON.parse(e.data);
          setTelemetry(data);
        } catch (error) {
          console.error("Errore nel parsing dei dati WebRTC:", error);
        }
      };

      pc.onicecandidate = (e) => {
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

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      client.publish(
        topicClient,
        JSON.stringify({
          type: offer.type,
          sdp: offer.sdp,
        }),
      );
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
        console.error("Errore nella ricezione della risposta signaling:", err);
      }
    });

    client.on("error", (err) => {
      console.error("Errore di connessione MQTT:", err);
      setStatus("disconnected");
    });
  };

  useEffect(() => {
    return () => {
      if (pcRef.current) {
        pcRef.current.close();
      }
    };
  }, []);

  const formatGear = (gear: number) => {
    if (gear === -1) return "R";
    if (gear === 0) return "N";
    return gear.toString();
  };

  const formatPedal = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  let mainContent;

  if (!isConnected) {
    mainContent = (
      <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 space-y-6">
        <AlertTriangle className="w-16 h-16 opacity-50" />
        <div className="text-center space-y-2">
          <p className="text-xl">
            In attesa di connessione ad Assetto Corsa...
          </p>
          <p className="text-sm opacity-70">
            Inserisci il PIN generato dal backend
          </p>
        </div>

        {/* PIN */}
        <div className="flex flex-col sm:flex-row items-center gap-4 mt-4">
          <input
            type="text"
            maxLength={6}
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))} // Only numbers
            placeholder="123456"
            className="bg-slate-900 border border-slate-700 text-center text-2xl tracking-widest font-mono text-slate-100 rounded-lg px-6 py-3 w-48 focus:outline-none focus:border-blue-500 transition-colors"
          />
          <button
            onClick={startConnection}
            disabled={status === "connecting" || pin.length !== 6}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors w-full sm:w-auto"
          >
            {status === "connecting" ? "Connessione..." : "Connetti"}
          </button>
        </div>
      </div>
    );
  } else if (!telemetry) {
    mainContent = (
      <div className="flex items-center justify-center h-[60vh] text-slate-500">
        <p className="text-xl animate-pulse">Ricezione dati P2P in corso...</p>
      </div>
    );
  } else {
    mainContent = (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Info */}
        <div className="col-span-full lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Car className="text-slate-400" />
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">
                Vettura
              </p>
              <p className="font-semibold">
                {telemetry.car_name || "Sconosciuta"}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-500 uppercase tracking-wider">
              Circuito
            </p>
            <p className="font-semibold capitalize">
              {telemetry.track_name || "Sconosciuto"}
            </p>
          </div>
        </div>

        {/* Speed */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center">
          <Gauge className="text-blue-500 w-10 h-10 mb-4 opacity-50" />
          <div className="text-6xl font-black tabular-nums tracking-tighter">
            {Math.round(telemetry.speed_kmh)}
          </div>
          <div className="text-slate-500 uppercase tracking-widest text-sm mt-2">
            km/h
          </div>
        </div>

        {/* Gear and RPM */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center">
          <div className="text-7xl font-black text-amber-400">
            {formatGear(telemetry.gear)}
          </div>
          <div className="text-slate-500 uppercase tracking-widest text-sm mt-2 font-mono">
            RPM: {Math.round(telemetry.engine_rpm)}
          </div>
          {/* RPM bar (Simplified, 8000 max rpm) */}
          <div className="w-full bg-slate-800 h-2 mt-4 rounded-full overflow-hidden">
            <div
              className="bg-amber-400 h-full transition-all duration-75"
              style={{
                width: `${Math.min((telemetry.engine_rpm / 8000) * 100, 100)}%`,
              }}
            ></div>
          </div>
        </div>

        {/* Pedals */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-center space-y-6">
          <div>
            <div className="flex justify-between text-sm mb-2 uppercase tracking-widest text-emerald-500">
              <span>Gas</span>
              <span>{formatPedal(telemetry.gas)}</span>
            </div>
            <div className="w-full bg-slate-800 h-4 rounded-sm overflow-hidden">
              <div
                className="bg-emerald-500 h-full transition-all duration-75"
                style={{ width: formatPedal(telemetry.gas) }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2 uppercase tracking-widest text-red-500">
              <span>Freno</span>
              <span>{formatPedal(telemetry.brake)}</span>
            </div>
            <div className="w-full bg-slate-800 h-4 rounded-sm overflow-hidden">
              <div
                className="bg-red-500 h-full transition-all duration-75"
                style={{ width: formatPedal(telemetry.brake) }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Activity className="text-blue-500 w-8 h-8" />
          <h1 className="text-2xl font-bold tracking-wider">
            VIRTUAL RACE ENGINEER
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${isConnected ? "bg-emerald-500 animate-pulse" : "bg-red-500"}`}
          ></div>
          <span className="text-sm font-medium text-slate-400 uppercase tracking-widest">
            {isConnected ? "Telemetry Active" : "Offline"}
          </span>
        </div>
      </header>

      {/* Main Content */}
      {mainContent}
    </div>
  );
}
