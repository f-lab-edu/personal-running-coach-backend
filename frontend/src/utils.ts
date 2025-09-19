// utils.ts
// Utility functions for the frontend

/**
 * Calculate pace (min/km) from distance (meters) and total time (seconds)
 * Returns a string in the format mm:ss
 */
export function calcPace(distance?: number, totalTime?: number): string | null {
  if (!distance || !totalTime || distance === 0) return null;
  // pace in seconds per km
  const paceSec = totalTime / (distance / 1000);
  const min = Math.floor(paceSec / 60);
  const sec = Math.round(paceSec % 60);
  return `${min}:${sec.toString().padStart(2, '0')}`;
}
