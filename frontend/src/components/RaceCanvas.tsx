import { useRef, useEffect, useState } from "react";
import type { TrackData, FrameUpdate } from "../types/simulations.ts";
import { useAnimationFrame } from "../hooks/useAnimationFrame.ts";

interface RaceCanvasProps {
  track: TrackData | null;
  frame: FrameUpdate | null;
  width?: number;
  height?: number;
}

function lerpAngle(a: number, b: number, t: number) {
  const d = b - a;
  const delta = ((d + Math.PI) % (Math.PI * 2)) - Math.PI;
  return a + delta * t;
}

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

export function RaceCanvas({
  track,
  frame,
  width = 1000,
  height = 800,
}: RaceCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const prevFrameRef = useRef<FrameUpdate | null>(null);
  const lastFrameTimeRef = useRef<number>(performance.now());

  const SERVER_TICK_MS = 1000 / 30;

  useEffect(() => {
    if (frame && frame !== prevFrameRef.current) {
      // Shift frames
      prevFrameRef.current = frame;
      lastFrameTimeRef.current = performance.now();
    }
  }, [frame]);

  useAnimationFrame((deltaTime) => {
    try {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      ctx.fillStyle = "#0a0a0f";
      ctx.fillRect(0, 0, width, height);

      if (!track) {
        ctx.fillStyle = "#555";
        ctx.font = "20px monospace";
        ctx.textAlign = "center";
        ctx.fillText("Waiting for server connection...", width / 2, height / 2);
        return;
      }

      if (!track.innerWalls || !track.outerWalls) {
        console.error("Track object is missing innerWalls or outerWalls", track);
        return;
      }

      ctx.strokeStyle = "rgba(100, 100, 180, 0.5)";
      ctx.lineWidth = 2;
      ctx.lineCap = "round";

      const allWalls = [...track.innerWalls, ...track.outerWalls];
      for (const wall of allWalls) {
        ctx.beginPath();
        ctx.moveTo(wall.x1, wall.y1);
        ctx.lineTo(wall.x2, wall.y2);
        ctx.stroke();
      }

      ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 8]);
      for (const cp of track.checkpoints) {
        ctx.beginPath();
        ctx.moveTo(cp.x1, cp.y1);
        ctx.lineTo(cp.x2, cp.y2);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      if (!frame) return;

      const now = performance.now();
      let timeSinceLastFrame = now - lastFrameTimeRef.current;
      if (timeSinceLastFrame < 0 || isNaN(timeSinceLastFrame)) {
        timeSinceLastFrame = 0;
      }

      const t = Math.max(0, Math.min(timeSinceLastFrame / SERVER_TICK_MS, 1.0));

      let bestCar = null;
      if (frame.bestCarIndex >= 0 && frame.bestCarIndex < frame.cars.length) {
        bestCar = frame.cars[frame.bestCarIndex];
      }

      if (bestCar && bestCar.alive && bestCar.sensorEndpoints) {
        ctx.strokeStyle = "rgba(0, 255, 170, 0.15)";
        ctx.lineWidth = 1;

        let visualX = bestCar.x;
        let visualY = bestCar.y;

        if (prevFrameRef.current && prevFrameRef.current.cars[frame.bestCarIndex]) {
          const prevBest = prevFrameRef.current.cars[frame.bestCarIndex];
          if (prevBest.alive) {
            visualX = lerp(prevBest.x, bestCar.x, t);
            visualY = lerp(prevBest.y, bestCar.y, t);
          }
        }

        for (const endpoint of bestCar.sensorEndpoints) {
          ctx.beginPath();
          ctx.moveTo(visualX, visualY);
          ctx.lineTo(endpoint.x, endpoint.y);
          ctx.stroke();
        }

        ctx.fillStyle = "rgba(0, 255, 170, 0.4)";
        for (const endpoint of bestCar.sensorEndpoints) {
          ctx.beginPath();
          ctx.arc(endpoint.x, endpoint.y, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      for (let i = 0; i < frame.cars.length; i++) {
        const car = frame.cars[i];

        let visualX = car.x;
        let visualY = car.y;
        let visualAngle = car.angle;

        if (prevFrameRef.current && prevFrameRef.current.cars[i]) {
          const prevCar = prevFrameRef.current.cars[i];

          if (car.alive && prevCar.alive) {
            const distSquared = (car.x - prevCar.x) ** 2 + (car.y - prevCar.y) ** 2;
            if (distSquared < 10000) {
              visualX = lerp(prevCar.x, car.x, t);
              visualY = lerp(prevCar.y, car.y, t);
              visualAngle = lerpAngle(prevCar.angle, car.angle, t);
            }
          }
        }

        ctx.save();
        ctx.translate(visualX, visualY);
        ctx.rotate(visualAngle);

        if (!car.alive) {
          ctx.globalAlpha = 0.04;
          ctx.fillStyle = "#ff4444";
        } else if (i === frame.bestCarIndex) {
          ctx.globalAlpha = 1.0;
          ctx.fillStyle = "#FFD700";
          ctx.shadowColor = "#FFD700";
          ctx.shadowBlur = 15;
        } else {
          ctx.globalAlpha = 0.3;
          ctx.fillStyle = "#00ff88";
        }

        const carLength = 24;
        const carWidth = 12;
        ctx.fillRect(-carLength / 2, -carWidth / 2, carLength, carWidth);

        ctx.shadowBlur = 0;
        ctx.restore();
      }

      const alive = frame.cars.filter((c) => c.alive).length;
      const total = frame.cars.length;

      ctx.globalAlpha = 1.0;
      ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
      ctx.fillRect(8, 8, 260, 72);

      ctx.fillStyle = "#ffffff";
      ctx.font = "13px monospace";
      ctx.textAlign = "left";
      ctx.fillText(`Generation: ${frame.generation}`, 16, 28);
      ctx.fillText(`Step: ${frame.step}`, 16, 46);
      ctx.fillText(`Alive: ${alive} / ${total}`, 16, 64);

      if (bestCar && bestCar.alive) {
        ctx.fillStyle = "#FFD700";
        ctx.fillText(`Best: ${bestCar.fitness.toFixed(0)}`, 150, 28);
      }
    } catch (err) {
      console.error("Canvas Render Error:", err);
    }
  });

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        border: "1px solid rgba(100, 100, 180, 0.3)",
        borderRadius: "12px",
        background: "#0a0a0f",
      }}
    />
  );
}
