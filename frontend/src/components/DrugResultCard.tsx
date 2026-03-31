import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import type { DrugResult } from '../types';
import { RiskGauge } from './RiskGauge';
import './DrugResultCard.css';

interface Props {
  result: DrugResult;
  index: number;
}

export function DrugResultCard({ result, index }: Props) {
  const [expanded, setExpanded] = useState(true);

  const risk = result.risk_level;
  const RiskIcon = risk === 'High' ? AlertTriangle : risk === 'Medium' ? Info : CheckCircle;

  return (
    <motion.div
      className={`drug-result-card risk-border-${risk.toLowerCase()}`}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      {/* Card Header */}
      <div className="drc-header" onClick={() => setExpanded(e => !e)} role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && setExpanded(v => !v)}>
        <div className="drc-drug-info">
          <div className="drc-drug-name-row">
            <RiskIcon size={18} style={{ color: result.risk_color }} />
            <h3 className="drc-drug-name">{result.drug}</h3>
            {!result.found_in_db && <span className="drc-unknown-badge">Limited Data</span>}
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
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
