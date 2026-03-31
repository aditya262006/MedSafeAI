import { motion } from 'framer-motion';
import { BarChart2, Brain, TrendingUp, TrendingDown } from 'lucide-react';
import type { DrugResult } from '../types';
import './ShapExplanation.css';

interface Props {
  results: DrugResult[];
}

const FEATURE_DESCRIPTIONS: Record<string, string> = {
  'Number of Side Effects': 'Total documented side effects',
  'Severity Score': 'Average severity on 1-10 scale',
  'Serious Adverse Event Rate': 'Rate of serious adverse events',
  'Drug Interaction Count': 'Number of known drug interactions',
  'Has Drug Interactions': 'Whether interactions exist',
  'Has High-Severity Interactions': 'Presence of high-severity interactions',
};

export function ShapExplanation({ results }: Props) {
  // Aggregate SHAP factors across all drug results
  const allFactors = results.flatMap(r => r.shap_explanation?.top_factors ?? []);
  if (allFactors.length === 0) return null;

  // Get the primary result (highest risk)
  const riskOrder = { High: 3, Medium: 2, Low: 1 };
  const primaryResult = [...results].sort((a, b) =>
    (riskOrder[b.risk_level] || 0) - (riskOrder[a.risk_level] || 0)
  )[0];

  const explanation = primaryResult?.shap_explanation;
  if (!explanation) return null;

  // Normalize contributions for bar display
  const maxAbs = Math.max(...explanation.top_factors.map(f => Math.abs(f.contribution)), 0.01);

  return (
    <motion.div
      className="shap-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="shap-header">
        <div className="shap-header-icon">
          <Brain size={20} />
        </div>
        <div>
          <h3 className="shap-title">AI Explainability (SHAP)</h3>
          <p className="shap-subtitle">Why the model made this prediction</p>
        </div>
        <BarChart2 size={18} className="shap-header-chart-icon" />
      </div>

      {/* Explanation Text */}
      <div className="shap-explanation-text">
        <p dangerouslySetInnerHTML={{
          __html: explanation.explanation_text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        }} />
      </div>

      {/* Factor bars */}
      <div className="shap-factors">
        <div className="shap-factors-label">
          <span>Feature</span>
          <span>Impact on Risk</span>
        </div>
        {explanation.top_factors.map((factor, i) => {
          const pct = Math.abs(factor.contribution) / maxAbs * 100;
          const isPositive = factor.contribution >= 0;
          return (
            <motion.div
              key={factor.feature}
              className="shap-factor-row"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="shap-factor-info">
                <span className="shap-feature-name">{factor.feature}</span>
                <span className="shap-feature-desc">{FEATURE_DESCRIPTIONS[factor.feature] || ''}</span>
              </div>

              <div className="shap-bar-area">
                <span className="shap-factor-value">{formatValue(factor.feature, factor.value)}</span>
                <div className="shap-bar-track">
                  <motion.div
                    className={`shap-bar-fill ${isPositive ? 'positive' : 'negative'} impact-${factor.impact}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.8, delay: 0.3 + i * 0.1, ease: 'easeOut' }}
                  />
                </div>
                <div className={`shap-impact-indicator ${factor.impact}`}>
                  {isPositive
                    ? <TrendingUp size={12} />
                    : <TrendingDown size={12} />
                  }
                  <span>{factor.impact}</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Base risk */}
      <div className="shap-base-risk">
        <span className="shap-base-label">Clinical Recommendation:</span>
        <span className="shap-base-text">{explanation.base_risk}</span>
      </div>

      {/* All drugs shap summary if multiple */}
      {results.length > 1 && (
        <div className="shap-all-drugs">
          <p className="shap-all-title">Risk Summary per Drug</p>
          <div className="shap-drug-summary-list">
            {results.map(r => (
              <div key={r.drug} className="shap-drug-summary-item">
                <span className="shap-drug-name-mini">{r.drug}</span>
                <span className={`shap-risk-mini risk-color-${r.risk_level.toLowerCase()}`}>
                  {r.risk_level} ({Math.round(r.risk_score * 100)}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

function formatValue(feature: string, value: number): string {
  if (feature === 'Serious Adverse Event Rate') return `${(value * 100).toFixed(1)}%`;
  if (feature === 'Has Drug Interactions' || feature === 'Has High-Severity Interactions') {
    return value === 1 ? 'Yes' : 'No';
  }
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(1);
}
