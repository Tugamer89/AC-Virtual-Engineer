import { useEffect, useState } from "react";
import { Activity, Gauge, Car, AlertTriangle } from "lucide-react";

// Definiamo esattamente cosa ci aspettiamo dal backend Python
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
  const [isConnected, setIsConnected] = useState<boolean>(false);

  useEffect(() => {
    // Connessione al backend locale (o IP di Windows se eseguito su dispositivi esterni)
    const ws = new WebSocket("ws://localhost:8080");

    ws.onopen = () => {
      console.log("Connesso al Virtual Engineer Backend");
      setIsConnected(true);
    };

    ws.onclose = () => {
      console.log("Disconnesso dal Backend");
      setIsConnected(false);
      setTelemetry(null);
    };

    ws.onmessage = (event) => {
      try {
        const data: TelemetryData = JSON.parse(event.data);
        setTelemetry(data);
      } catch (error) {
        console.error("Errore nel parsing dei dati:", error);
      }
    };

    // Cleanup alla disconnessione
    return () => {
      ws.close();
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

      {}
      {!isConnected ? (
        <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 space-y-4">
          <AlertTriangle className="w-16 h-16 opacity-50" />
          <p className="text-xl">
            In attesa di connessione ad Assetto Corsa...
          </p>
          <p className="text-sm opacity-70">
            Assicurati che il backend Python sia in esecuzione (server.py)
          </p>
        </div>
      ) : !telemetry ? (
        <div className="flex items-center justify-center h-[60vh] text-slate-500">
          <p className="text-xl animate-pulse">Ricezione dati in corso...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card Info Sessione */}
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

          {/* Card Velocità */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center">
            <Gauge className="text-blue-500 w-10 h-10 mb-4 opacity-50" />
            <div className="text-6xl font-black tabular-nums tracking-tighter">
              {Math.round(telemetry.speed_kmh)}
            </div>
            <div className="text-slate-500 uppercase tracking-widest text-sm mt-2">
              km/h
            </div>
          </div>

          {/* Card Marcia e RPM */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center">
            <div className="text-7xl font-black text-amber-400">
              {formatGear(telemetry.gear)}
            </div>
            <div className="text-slate-500 uppercase tracking-widest text-sm mt-2 font-mono">
              RPM: {Math.round(telemetry.engine_rpm)}
            </div>
            {/* Barra RPM (Semplificata, supponendo 8000 rpm max) */}
            <div className="w-full bg-slate-800 h-2 mt-4 rounded-full overflow-hidden">
              <div
                className="bg-amber-400 h-full transition-all duration-75"
                style={{
                  width: `${Math.min((telemetry.engine_rpm / 8000) * 100, 100)}%`,
                }}
              ></div>
            </div>
          </div>

          {/* Card Pedali */}
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
      )}
    </div>
  );
}
