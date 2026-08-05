import axios from 'axios';
import type { PredictResponse, SearchResponse } from './types';

const RENDER_API_URL = 'https://medsafeai-api.onrender.com';
const BASE_URL = (import.meta.env.VITE_API_URL || RENDER_API_URL).replace(/\/+$/, '');

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
  const res = await api.get<SearchResponse>('/api/search', { params: { q: query } });
  return res.data;
}

export async function predictRisk(drugs: string[]): Promise<PredictResponse> {
  const res = await api.post('/api/predict', { drugs });
  const data = res.data as {
    results?: Array<Record<string, unknown>>;
    interactions?: Array<Record<string, unknown>>;
    overall_risk?: 'Low' | 'Medium' | 'High';
    combined_risk?: 'Low' | 'Medium' | 'High';
    summary?: string;
  };

  const combinedRisk = data.combined_risk ?? data.overall_risk ?? 'Low';
  const interactions = (data.interactions ?? []).map((item) => ({
    drug_a: String(item.drug_a ?? ''),
    drug_b: String(item.drug_b ?? ''),
    severity: (item.severity as 'Low' | 'Medium' | 'High') ?? 'High',
    description: String(item.description ?? 'Potential interaction detected.'),
    severity_color: String(item.severity_color ?? '#ef4444'),
  }));

  const results = (data.results ?? []).map((item) => {
    const risk = (item.risk_level as 'Low' | 'Medium' | 'High') ?? 'Low';
    const score = Number(item.risk_score ?? (risk === 'High' ? 0.85 : risk === 'Medium' ? 0.55 : 0.25));
    return {
      drug: String(item.drug ?? ''),
      found_in_db: Boolean(item.found_in_db ?? item.found ?? true),
      risk_level: risk,
      risk_score: score,
      risk_color: risk === 'High' ? '#ef4444' : risk === 'Medium' ? '#f59e0b' : '#10b981',
      side_effects: Array.isArray(item.side_effects) ? item.side_effects.map(String) : [],
      severity_score: Number(item.severity_score ?? 0),
      serious_event_rate: Number(item.serious_event_rate ?? 0),
      shap_explanation: null,
    };
  });

  return {
    results,
    interactions,
    combined_risk: combinedRisk,
    combined_risk_color: combinedRisk === 'High' ? '#ef4444' : combinedRisk === 'Medium' ? '#f59e0b' : '#10b981',
    summary: data.summary ?? `Analysis complete for ${drugs.join(', ')}. Overall risk is ${combinedRisk}.`,
  };
}

export async function checkHealth(): Promise<{ status: string; model_loaded: boolean }> {
  const res = await api.get('/api/health');
  return res.data;
}
