import { useSimulation } from "./hooks/useSimulations";
import { RaceCanvas } from "./components/RaceCanvas";
import { Controls } from "./components/Controls";
import { StatsPanel } from "./components/StatsPanel";

function App() {
  const { track, frame, stats, connected, send } = useSimulation();

  return (
    <div style={styles.app}>
      <h1 style={styles.header}>
        🏎️ <span style={styles.headerAccent}>Something F1</span> — Neural Evolution Racing
      </h1>

      <div style={styles.layout}>
        <div style={styles.canvasArea}>
          <RaceCanvas track={track} frame={frame} width={1000} height={800} />
        </div>

        <div style={styles.sidebar}>
          <Controls connected={connected} send={send} />
          <StatsPanel stats={stats} />
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: "100vh",
    backgroundColor: "#050508",
    color: "#fff",
    padding: "24px",
    fontFamily: "'Inter', system-ui, sans-serif",
  },
  header: {
    fontSize: "24px",
    fontWeight: "bold",
    marginBottom: "20px",
    fontFamily: "monospace",
  },
  headerAccent: {
    background: "linear-gradient(90deg, #FFD700, #ff6b35)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  layout: {
    display: "flex",
    gap: "20px",
    alignItems: "flex-start",
  },
  canvasArea: {
    flexShrink: 0,
  },
  sidebar: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    minWidth: "320px",
    maxWidth: "400px",
  },
};

export default App;
