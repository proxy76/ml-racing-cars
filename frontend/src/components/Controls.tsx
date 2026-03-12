import { useState } from "react";
import type { ClientCommand } from "../types/simulations";

interface ControlsProps {
    connected: boolean;                   // Is the WebSocket connected?
    send: (cmd: ClientCommand) => void;  // Function to send commands to server
}

export function Controls({ connected, send }: ControlsProps) {

    const [running, setRunning] = useState(false);

    const [speed, setSpeed] = useState(1);

    const handleStartPause = () => {
        if (!running) {
            send({ type: running ? "resume" : "start" });
            setRunning(true);
        } else {
            send({ type: "pause" });
            setRunning(false);
        }
    };

    const handleReset = () => {
        send({ type: "reset" });
        setRunning(false);
        setSpeed(1);
    };

    const handleSpeedChange = (newSpeed: number) => {
        setSpeed(newSpeed);
        send({ type: "set_speed", speed: newSpeed });
    };

    return (
        <div style={styles.container}>
            {/* Connection status indicator */}
            <div style={styles.status}>
                <span
                    style={{
                        ...styles.statusDot,
                        backgroundColor: connected ? "#00ff88" : "#ff4444",
                    }}
                />
                {connected ? "Connected" : "Disconnected"}
            </div>

            {/* Main control buttons */}
            <div style={styles.buttons}>
                <button
                    onClick={handleStartPause}
                    disabled={!connected}
                    style={{
                        ...styles.button,
                        backgroundColor: running ? "#ff6b35" : "#00cc6a",
                    }}
                >
                    {running ? "⏸ Pause" : "▶ Start"}
                </button>

                <button
                    onClick={handleReset}
                    disabled={!connected}
                    style={{ ...styles.button, backgroundColor: "#6366f1" }}
                >
                    🔄 Reset
                </button>
            </div>

            {/* Speed slider */}
            <div style={styles.speedControl}>
                <label style={styles.label}>
                    Speed: {speed}x
                </label>
                <input
                    type="range"
                    min={1}
                    max={50}
                    value={speed}
                    onChange={(e) => handleSpeedChange(Number(e.target.value))}
                    style={styles.slider}
                />
            </div>
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    container: {
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        padding: "20px",
        backgroundColor: "rgba(15, 15, 25, 0.9)",
        borderRadius: "12px",
        border: "1px solid rgba(100, 100, 180, 0.3)",
    },
    status: {
        display: "flex",
        alignItems: "center",
        gap: "8px",
        color: "#aaa",
        fontSize: "13px",
        fontFamily: "monospace",
    },
    statusDot: {
        width: "8px",
        height: "8px",
        borderRadius: "50%",
        display: "inline-block",
    },
    buttons: {
        display: "flex",
        gap: "10px",
    },
    button: {
        padding: "10px 20px",
        border: "none",
        borderRadius: "8px",
        color: "#fff",
        fontSize: "14px",
        fontWeight: "bold",
        cursor: "pointer",
        fontFamily: "monospace",
        transition: "opacity 0.2s",
    },
    speedControl: {
        display: "flex",
        flexDirection: "column",
        gap: "6px",
    },
    label: {
        color: "#ccc",
        fontSize: "13px",
        fontFamily: "monospace",
    },
    slider: {
        width: "100%",
        accentColor: "#6366f1",
    },
};
