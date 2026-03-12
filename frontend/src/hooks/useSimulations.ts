import { useRef, useState, useCallback, useEffect } from "react";
import type {
    TrackData,
    FrameUpdate,
    GenerationResult,
    ClientCommand,
} from "../types/simulations";

const WS_URL = "ws://localhost:8000/ws";

export function useSimulation() {

    const [track, setTrack] = useState<TrackData | null>(null);

    const [frame, setFrame] = useState<FrameUpdate | null>(null);

    const [stats, setStats] = useState<GenerationResult[]>([]);

    // Connection status
    const [connected, setConnected] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const socket = new WebSocket(WS_URL);

        socket.onopen = () => {
            console.log("Connected to simulation server");
            setConnected(true);
            socket.send(JSON.stringify({ type: "get_track" }));
        };

        socket.onclose = () => {
            console.log("Disconnected from simulation server");
            setConnected(false);
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        socket.onmessage = (event: MessageEvent) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case "track":
                    setTrack(data as TrackData);
                    console.log("Received track geometry");
                    break;

                case "frame":
                    setFrame(data as FrameUpdate);
                    break;

                case "generation_end":
                    setStats((prev) => [...prev, data as GenerationResult]);
                    break;

                default:
                    console.warn("Unknown message type:", data.type);
            }
        };

        wsRef.current = socket;

        return () => {
            if (wsRef.current === socket) {
                console.log("Cleaning up active WebSocket connection");
                socket.close();
                wsRef.current = null;
            } else {
                console.log("Cleaning up stale WebSocket connection (React StrictMode)");
                socket.close();
            }
        };
    }, []);
    const send = useCallback((command: ClientCommand) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(command));
        } else {
            console.warn("Cannot send command: WebSocket not connected");
        }
    }, []);

    return { track, frame, stats, connected, send };
}
