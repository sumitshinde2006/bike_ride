// API utility for backend communication

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PredictionInputs {
  season: string;
  hour?: string;
  month?: string;
  weekday?: string;
  weather: string;
  temperature: string;
  humidity: string;
  workingDay: string;
}

export interface PredictionResponse {
  prediction: number;
  success: boolean;
  error?: string;
}

export interface HealthResponse {
  status: string;
  hour_model_loaded: boolean;
  day_model_loaded: boolean;
}

/**
 * Check if the backend server is healthy
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Get prediction from the backend ML model
 */
export async function getPrediction(
  inputs: PredictionInputs,
  isHourly: boolean
): Promise<PredictionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        inputs,
        isHourly,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Prediction failed');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Prediction error:', error);
    return {
      prediction: 0,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

