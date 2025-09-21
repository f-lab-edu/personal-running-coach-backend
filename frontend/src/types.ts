// ConnectPage
export interface ConnectPageProps {
//   user: any;
  thirdList: string[];
}

// TrainingDetailPage
export interface StreamData {
  heartrate?: number[];
  cadence?: number[];
  distance?: number[];
  velocity?: number[];
  altitude?: number[];
  time?: number[];
  [key: string]: number[] | undefined;
}

export interface TrainDetail {
  session_id: string;
  train_date: string;
  distance?: number;
  avg_speed?: number;
  total_time?: number;
  analysis_result?: string;
  stream?: StreamData;
  [key: string]: any;
}

// TrainingPage
export interface TrainResponse {
  session_id: string;
  train_date: string;
  distance?: number;
  avg_speed?: number;
  total_time?: number;
  activity_title?: string;
  analysis_result?: string;
}

export interface TrainingPageProps {
//   user: any;
  token: any;
}

// UserPage
export type UserInfoData = {
  height?: number;
  weight?: number;
  age?: number;
  sex?: string;
  train_goal?: string;
};

export type Profile = {
  id: string;
  email: string;
  name?: string;
  provider: string;
  info?: UserInfoData;
};
// src/types.ts
// Centralized type definitions for the frontend

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
