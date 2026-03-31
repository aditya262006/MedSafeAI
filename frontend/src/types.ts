// Shared TypeScript types for the AI Side Effect Checker

export interface ShapFactor {
  feature: string;
  value: number;
  impact: 'low' | 'medium' | 'high';
  contribution: number;
}

export interface ShapExplanation {
  top_factors: ShapFactor[];
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
  shap_explanation: ShapExplanation | null;
}

export interface Interaction {
  drug_a: string;
  drug_b: string;
  severity: 'Low' | 'Medium' | 'High';
  description: string;
  severity_color: string;
}

export interface PredictResponse {
  results: DrugResult[];
  interactions: Interaction[];
  combined_risk: 'Low' | 'Medium' | 'High';
  combined_risk_color: string;
  summary: string;
}

export interface SearchResponse {
  suggestions: string[];
  query: string;
}

export type RiskLevel = 'Low' | 'Medium' | 'High';
