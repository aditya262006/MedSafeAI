import { motion } from 'framer-motion';
import { Activity, TrendingUp, TrendingDown } from 'lucide-react';
import type { DrugResult } from '../types';
import './RiskFactorPanel.css';

interface Props {
  results: DrugResult[];
}

const FEATURE_DESCRIPTIONS: Record<string, string> = {
  'Number of Side Effects': 'Total documented side effects',
  'Severity Score': 'Average severity on 1–10 scale',
  'Serious Adverse Event Rate': 'Rate of serious adverse events',
  'Drug Interaction Count': 'Number of known drug interactions',
  'Has Drug Interactions': 'Whether interactions exist',
  'Has High-Severity Interactions': 'Presence of high-severity interactions',
};

export function RiskFactorPanel({ results }: Props) {
  // Get the primary result (highest risk)
  const riskOrder = { High: 3, Medium: 2, Low: 1 };
  const primaryResult = [...results].sort((a, b) =>
    (riskOrder[b.risk_level] || 0) - (riskOrder[a.risk_level] || 0)
  )[0];

  const factors = primaryResult?.clinical_factors;
  if (!factors || factors.top_factors.length === 0) return null;

  // Normalize contributions for bar display
  const maxAbs = Math.max(...factors.top_factors.map(f => Math.abs(f.contribution)), 0.01);

  return (
    <motion.div
      className="rfp-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="rfp-header">
        <div className="rfp-header-icon">
          <Activity size={18} />
        </div>
        <div>
          <h3 className="rfp-title">Risk Factor Analysis</h3>
          <p className="rfp-subtitle">Clinical factors influencing risk assessment</p>
        </div>
      </div>

      {/* Explanation Text */}
      <div className="rfp-explanation">
        <p dangerouslySetInnerHTML={{
          __html: factors.explanation_text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        }} />
      </div>

      {/* Factor bars */}
      <div className="rfp-factors">
        <div className="rfp-factors-header">
          <span>Factor</span>
          <span>Impact</span>
        </div>
        {factors.top_factors.map((factor, i) => {
          const pct = Math.abs(factor.contribution) / maxAbs * 100;
          const isPositive = factor.contribution >= 0;
          return (
            <motion.div
              key={factor.feature}
              className="rfp-factor-row"
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <div className="rfp-factor-info">
                <span className="rfp-feature-name">{factor.feature}</span>
                <span className="rfp-feature-desc">{FEATURE_DESCRIPTIONS[factor.feature] || ''}</span>
              </div>

              <div className="rfp-bar-area">
                <span className="rfp-factor-value">{formatValue(factor.feature, factor.value)}</span>
                <div className="rfp-bar-track">
                  <motion.div
                    className={`rfp-bar-fill impact-${factor.impact}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.7, delay: 0.2 + i * 0.08, ease: 'easeOut' }}
                  />
                </div>
                <div className={`rfp-impact-badge impact-${factor.impact}`}>
                  {isPositive
                    ? <TrendingUp size={11} />
                    : <TrendingDown size={11} />
                  }
                  <span>{factor.impact}</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Clinical recommendation */}
      <div className="rfp-recommendation">
        <span className="rfp-rec-label">Recommendation</span>
        <span className="rfp-rec-text">{factors.base_risk}</span>
      </div>

      {/* Multi-drug summary */}
      {results.length > 1 && (
        <div className="rfp-drug-summary">
          <p className="rfp-summary-title">Per-Drug Risk</p>
          <div className="rfp-summary-list">
            {results.map(r => (
              <div key={r.drug} className="rfp-summary-item">
                <span className="rfp-summary-drug">{r.drug}</span>
                <span className={`rfp-summary-risk risk-color-${r.risk_level.toLowerCase()}`}>
                  {r.risk_level} · {Math.round(r.risk_score * 100)}%
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
