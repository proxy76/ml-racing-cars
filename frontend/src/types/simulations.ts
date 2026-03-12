export interface WallSegment {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export interface TrackData {
    type: "track";
    innerWalls: WallSegment[];
    outerWalls: WallSegment[];
    checkpoints: WallSegment[];
    startPos: { x: number; y: number };
    startAngle: number;
}

export interface CarState {
    x: number;
    y: number;
    angle: number;
    alive: boolean;
    fitness: number;
    speed: number;
    sensors: number[];
    sensorEndpoints: { x: number; y: number }[];
}

export interface FrameUpdate {
    type: "frame";
    generation: number;
    step: number;
    cars: CarState[];
    bestCarIndex: number;
}

export interface GenerationResult {
    type: "generation_end";
    generation: number;
    bestFitness: number;
    avgFitness: number;
    worstFitness: number;
    bestCheckpoints: number;
    bestDistance: number;
    bestStepsAlive: number;
    allTimeBest: number;
}

export type ClientCommand =
    | { type: "start" }
    | { type: "pause" }
    | { type: "resume" }
    | { type: "reset" }
    | { type: "set_speed"; speed: number };
