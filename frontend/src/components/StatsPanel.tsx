import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
} from "recharts";
import type { GenerationResult } from "../types/simulations";

interface StatsPanelProps {
    stats: GenerationResult[];  // Array of generation results (grows over time)
}

export function StatsPanel({ stats }: StatsPanelProps) {
    const chartData = stats.map((s) => ({
        gen: s.generation,               // X-axis: generation number
        best: Math.round(s.bestFitness), // Gold line
        avg: Math.round(s.avgFitness),   // Green line
    }));

    // Get the latest generation's stats for the info panel
    const latest = stats[stats.length - 1];

    return (
        <div style={styles.container}>
            <h3 style={styles.title}>📊 Training Progress</h3>

            {/* Stats summary for the latest generation */}
            {latest && (
                <div style={styles.statsGrid}>
                    <div style={styles.stat}>
                        <span style={styles.statLabel}>Generation</span>
                        <span style={styles.statValue}>{latest.generation}</span>
                    </div>
                    <div style={styles.stat}>
                        <span style={styles.statLabel}>Best Fitness</span>
                        <span style={{ ...styles.statValue, color: "#FFD700" }}>
                            {Math.round(latest.bestFitness)}
                        </span>
                    </div>
                    <div style={styles.stat}>
                        <span style={styles.statLabel}>Avg Fitness</span>
                        <span style={{ ...styles.statValue, color: "#00ff88" }}>
                            {Math.round(latest.avgFitness)}
                        </span>
                    </div>
                    <div style={styles.stat}>
                        <span style={styles.statLabel}>All-Time Best</span>
                        <span style={{ ...styles.statValue, color: "#ff6b35" }}>
                            {Math.round(latest.allTimeBest)}
                        </span>
                    </div>
                    <div style={styles.stat}>
                        <span style={styles.statLabel}>Best Checkpoints</span>
                        <span style={styles.statValue}>{latest.bestCheckpoints}</span>
                    </div>
                </div>
            )}

            {/* Fitness chart */}
            {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                        {/* Subtle grid lines */}
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />

                        {/* X-axis: generation number */}
                        <XAxis
                            dataKey="gen"
                            stroke="#555"
                            fontSize={11}
                            tickLine={false}
                        />

                        {/* Y-axis: fitness score */}
                        <YAxis
                            stroke="#555"
                            fontSize={11}
                            tickLine={false}
                            width={60}
                        />

                        {/* Tooltip on hover — shows exact values */}
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "rgba(10, 10, 20, 0.9)",
                                border: "1px solid rgba(100, 100, 180, 0.3)",
                                borderRadius: "8px",
                                fontSize: "12px",
                            }}
                        />

                        {/* Best fitness line (gold) */}
                        <Line
                            type="monotone"
                            dataKey="best"
                            stroke="#FFD700"
                            strokeWidth={2}
                            dot={false}            // No dots on each data point (cleaner)
                            name="Best Fitness"
                        />

                        {/* Average fitness line (green) */}
                        <Line
                            type="monotone"
                            dataKey="avg"
                            stroke="#00ff88"
                            strokeWidth={1.5}
                            dot={false}
                            name="Avg Fitness"
                        />
                    </LineChart>
                </ResponsiveContainer>
            ) : (
                <p style={{ color: "#555", fontSize: "13px", fontFamily: "monospace" }}>
                    Start the simulation to see training progress...
                </p>
            )}
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    container: {
        padding: "20px",
        backgroundColor: "rgba(15, 15, 25, 0.9)",
        borderRadius: "12px",
        border: "1px solid rgba(100, 100, 180, 0.3)",
    },
    title: {
        color: "#fff",
        fontSize: "16px",
        fontFamily: "monospace",
        margin: "0 0 16px 0",
    },
    statsGrid: {
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: "12px",
        marginBottom: "16px",
    },
    stat: {
        display: "flex",
        flexDirection: "column",
        gap: "4px",
    },
    statLabel: {
        color: "#777",
        fontSize: "11px",
        fontFamily: "monospace",
        textTransform: "uppercase",
    },
    statValue: {
        color: "#fff",
        fontSize: "18px",
        fontWeight: "bold",
        fontFamily: "monospace",
    },
};
