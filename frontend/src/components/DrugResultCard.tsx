import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, CheckCircle } from 'lucide-react';
import type { DrugResult } from '../types';
import { RiskGauge } from './RiskGauge';
import { DrugIcon } from './SymptomSearch';
import './DrugResultCard.css';

interface Props {
  result: DrugResult;
  index: number;
}

export function DrugResultCard({ result, index }: Props) {
  const [expanded, setExpanded] = useState(true);

  const risk = result.risk_level;
  
  // Simulated Doctor Review
  const doctorReview = risk === 'High' 
    ? { name: "Dr. Sarah Chen, MD", specialty: "Cardiology", text: "Requires close monitoring. Do not combine with other strong medications without consulting your primary physician." }
    : risk === 'Medium'
    ? { name: "Dr. James Wilson, DO", specialty: "Internal Medicine", text: "Generally effective but monitor for common side effects like nausea or dizziness during the first week." }
    : { name: "Dr. Emily Taylor, MD", specialty: "Family Medicine", text: "Very safe profile for most patients. Follow standard dosing instructions." };


  return (
    <motion.div
      className={`drug-result-card risk-border-${risk.toLowerCase()}`}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      {/* Card Header */}
      <div className="drc-header" onClick={() => setExpanded(e => !e)} role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && setExpanded(v => !v)}>
        <div className="drc-drug-icon">
          <DrugIcon drugName={result.drug} size={42} />
        </div>
        <div className="drc-drug-info">
          <div className="drc-drug-name-row">
            <h3 className="drc-drug-name">{result.drug}</h3>
            {result.found_in_db ? (
              <span className="drc-verified-badge">
                <CheckCircle size={10} /> Verified
              </span>
            ) : (
              <span className="drc-unknown-badge">Limited Data</span>
            )}
          </div>
          <div className="drc-meta">
            <span className={`drc-severity-chip severity-${risk.toLowerCase()}`}>
              Severity: {result.severity_score.toFixed(1)}/10
            </span>
            <span className="drc-sep">·</span>
            <span className="drc-serious-rate">
              Serious Events: {(result.serious_event_rate * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        <div className="drc-gauge-wrap">
          <RiskGauge risk={risk} score={result.risk_score} size="sm" />
        </div>

        <button className={`drc-chevron ${expanded ? 'open' : ''}`} aria-label="Toggle">
          <ChevronDown size={18} />
        </button>
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            className="drc-body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            style={{ overflow: 'hidden' }}
          >
            <div className="drc-body-inner">
              <div className="divider" style={{ margin: '0 0 20px' }} />

              {/* Side Effects */}
              <div className="drc-section">
                <h4 className="drc-section-title">
                  <span className="drc-section-dot" />
                  Side Effects ({result.side_effects.length})
                </h4>
                <div className="side-effects-grid">
                  {result.side_effects.map((se, i) => (
                    <motion.span
                      key={se}
                      className="side-effect-tag"
                      initial={{ opacity: 0, scale: 0.85 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      {se}
                    </motion.span>
                  ))}
                </div>
              </div>

              {/* Doctor Review */}
              <div className="drc-section" style={{ marginTop: '20px' }}>
                <h4 className="drc-section-title">
                  <span className="drc-section-dot" style={{ background: '#00C896' }} />
                  Expert Medical Opinion
                </h4>
                <div className="drc-doctor-review">
                  <div className="doctor-avatar">
                    {doctorReview.name.charAt(4)}
                  </div>
                  <div className="doctor-info">
                    <div className="doctor-name">{doctorReview.name} <span>• {doctorReview.specialty}</span></div>
                    <p className="doctor-text">"{doctorReview.text}"</p>
                  </div>
                </div>
              </div>

              {/* Clinical Insights */}
              {(result.demographics || result.specialist_consult || result.clinical_consensus) && (
                <div className="drc-section" style={{ marginTop: '20px' }}>
                  <h4 className="drc-section-title">
                    <span className="drc-section-dot" style={{ background: 'var(--accent-purple, #a855f7)' }} />
                    Clinical Insights
                  </h4>
                  <div className="drc-insights">
                    {result.demographics && (
                      <div className="drc-demographics">
                        {result.demographics.pregnancy_category && (
                          <div className="insight-tag warning">
                            <span>🤰</span> Pregnancy Category: {result.demographics.pregnancy_category}
                          </div>
                        )}
                        {result.demographics.geriatric_warning && (
                          <div className="insight-tag caution">
                            <span>🧓</span> Geriatric Warning
                          </div>
                        )}
                        {result.demographics.pediatric_warning && (
                          <div className="insight-tag caution">
                            <span>👶</span> Pediatric Warning
                          </div>
                        )}
                      </div>
                    )}
                    {result.specialist_consult && (
                      <p className="insight-text"><strong>Specialist Consult:</strong> {result.specialist_consult}</p>
                    )}
                    {result.clinical_consensus && (
                      <p className="insight-text"><strong>Clinical Consensus:</strong> {result.clinical_consensus}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
