import axios from 'axios';
import type { PredictResponse, SearchResponse } from './types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

console.log('[MedSafeAI] API Base URL:', BASE_URL);

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[MedSafeAI] API Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
    });
    return Promise.reject(error);
  }
);

export async function searchDrugs(query: string): Promise<SearchResponse> {
  const res = await api.get<SearchResponse>('/search', { params: { q: query } });
  return res.data;
}

export async function predictRisk(drugs: string[]): Promise<PredictResponse> {
  const res = await api.post<PredictResponse>('/predict', { drugs });
  return res.data;
}

export async function checkHealth(): Promise<{ status: string; model_loaded: boolean }> {
  const res = await api.get('/health');
  return res.data;
}
