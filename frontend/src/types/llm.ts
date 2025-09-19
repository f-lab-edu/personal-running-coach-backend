// Types for LLMResponse and LLMSessionResult based on backend models.py
export interface LLMSessionResult {
  day: string;
  workout_type: string;
  distance_km: number;
  pace?: string;
  notes?: string;
}

export interface LLMResponse {
  sessions?: LLMSessionResult[];
  advice?: string;
}
