// Shared TypeScript types for the AI Side Effect Checker

export interface ClinicalFactor {
  feature: string;
  value: number;
  impact: 'low' | 'medium' | 'high';
  contribution: number;
}

export interface ClinicalFactors {
  top_factors: ClinicalFactor[];
  explanation_text: string;
  base_risk: string;
}

export interface DrugResult {
  drug: string;
  found_in_db: boolean;
  risk_level: 'Low' | 'Medium' | 'High';
  risk_score: number;
  risk_color: string;
  side_effects: string[];
  severity_score: number;
  serious_event_rate: number;
  clinical_factors?: ClinicalFactors;
  demographics?: {
    pregnancy_category: string;
    geriatric_warning: boolean;
    pediatric_warning: boolean;
  };
  specialist_consult?: string;
  clinical_consensus?: string;
}

export interface Interaction {
  drug_a: string;
  drug_b: string;
  severity: 'Low' | 'Medium' | 'High';
  description: string;
  severity_color: string;
  evidence_level?: string;
  verified_source?: string;
}

export interface PredictResponse {
  results: DrugResult[];
  interactions: Interaction[];
  combined_risk: 'Low' | 'Medium' | 'High';
  combined_risk_color: string;
  summary: string;
  consultation_suggestion: string;
}

export interface SearchResponse {
  suggestions: string[];
  query: string;
}

export type RiskLevel = 'Low' | 'Medium' | 'High';

// ── Additional Types ──────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface SymptomResult {
  symptom?: string;
  drugs: string[];
  severity: string;
  consult_doctor: boolean;
  advice: string;
}
