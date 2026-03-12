import { useRef, useEffect } from "react";

/**
 * A custom hook that runs a callback on every browser Repaint (via requestAnimationFrame).
 * It automatically handles pausing when the component is unmounted.
 */
export function useAnimationFrame(callback: (deltaTime: number) => void) {
  const requestRef = useRef<number>(0);
  const previousTimeRef = useRef<number>(0);

  // Store the callback in a ref so we don't have to restart the loop on every render
  const callbackRef = useRef(callback);
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    const animate = (time: number) => {
      if (previousTimeRef.current !== undefined) {
        const deltaTime = time - previousTimeRef.current;
        callbackRef.current(deltaTime);
      }
      previousTimeRef.current = time;
      requestRef.current = requestAnimationFrame(animate);
    };

    requestRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, []); // Run once on mount
}
