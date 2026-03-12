from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from simulation.world import World

app = FastAPI(
    title="ML Car Racing Simulation",
    description="Neural network cars learn to race through evolution"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)


@app.get("/health")
async def health_check():
    return {"status": "running", "message": "ML Car Racing backend is alive!"}

@app.websocket("/ws")
async def simulation_websocket(ws: WebSocket):
    await ws.accept()
    print("Frontend connected via WebSocket!")


    world = World(pop_size=100)

    track_data = world.get_track_data()
    await ws.send_json(track_data)
    print(f"Sent track: {len(track_data['innerWalls'])} inner walls, "
          f"{len(track_data['outerWalls'])} outer walls, "
          f"{len(track_data['checkpoints'])} checkpoints")

    running = False 
    speed = 1 # Speed multiplier (1 = real-time, 10 = 10x fast)
    render_skip = 1   

    sim_task = None

    async def simulation_loop():
        nonlocal running
        import time

        # Target 30 FPS for sending data to the browser
        # The frontend handles interpolation/animations so 30 is plenty
        target_render_fps = 30
        render_interval = 1.0 / target_render_fps
        last_render_time = time.time()

        while running:
            # Process multiple physics steps per loop iteration based on speed.
            # E.g., speed=1 -> 1 step. speed=50 -> 50 steps.
            # This completely decouples physics calculations from the event loop delay.
            steps_to_run = speed 
            still_going = True
            
            for _ in range(steps_to_run):
                still_going = world.step()
                if not still_going:
                    break
            
            # Check if it's time to send a frame to the frontend
            current_time = time.time()
            if current_time - last_render_time >= render_interval:
                try:
                    frame_data = world.get_frame_data()
                    await ws.send_json(frame_data)
                    last_render_time = current_time
                except WebSocketDisconnect:
                    running = False
                    return

            # Yield control back to the FastAPI event loop so it can handle
            # incoming WebSocket messages (like pause/speed changes) instantly.
            # If speed is 1, simulate real-time delay (roughly 60 physics steps per sec)
            if speed == 1:
                await asyncio.sleep(0.016)
            else:
                await asyncio.sleep(0)  # Yield without delaying

            # Handle end of generation
            if not still_going:
                if running:
                    stats = world.evolve_generation()
                    try:
                        await ws.send_json(stats)
                        print(f"🧬 Gen {stats['generation']}: "
                              f"best={stats['bestFitness']}, "
                              f"avg={stats['avgFitness']}, "
                              f"checkpoints={stats['bestCheckpoints']}")
                    except WebSocketDisconnect:
                        running = False
                        return

    try:
        while True:
            raw = await ws.receive_text()
            message = json.loads(raw)
            cmd = message.get("type", "")

            if cmd == "start" and not running:
                
                print("Starting simulation")
                running = True
                
                sim_task = asyncio.create_task(simulation_loop())

            elif cmd == "pause":
                print("Pausing simulation")
                running = False
                if sim_task:
                    await sim_task
                    sim_task = None

            elif cmd == "resume" and not running:
                print("Resuming simulation")
                running = True
                sim_task = asyncio.create_task(simulation_loop())

            elif cmd == "set_speed":
                new_speed = message.get("speed", 1)
                speed = max(1, min(100, new_speed))
                render_skip = max(1, speed // 3)
                print(f"Speed set to {speed}x (sending every {render_skip} frames)")

            elif cmd == "reset":
                print("Resetting simulation")
                running = False
                if sim_task:
                    await sim_task
                    sim_task = None
                world = World(pop_size=100)
                await ws.send_json(world.get_track_data())
                await ws.send_json(world.get_frame_data()) # Send initial frame so it's not blank
                print("Reset complete, new track sent")

            elif cmd == "get_track":
                print("Resending track data requested by client")
                await ws.send_json(world.get_track_data())
                await ws.send_json(world.get_frame_data())

    except WebSocketDisconnect:
        running = False
        if sim_task:
            sim_task.cancel()
        print("Frontend disconnected")
