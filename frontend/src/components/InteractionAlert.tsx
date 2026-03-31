import { motion } from 'framer-motion';
import { AlertTriangle, Zap, Info } from 'lucide-react';
import type { Interaction } from '../types';
import './InteractionAlert.css';

interface Props {
  interactions: Interaction[];
}

const SEVERITY_ICONS = {
  High: AlertTriangle,
  Medium: Zap,
  Low: Info,
};

export function InteractionAlert({ interactions }: Props) {
  if (interactions.length === 0) {
    return (
      <motion.div
        className="no-interaction-box"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <span className="no-int-icon">✓</span>
        <div>
          <p className="no-int-title">No Drug Interactions Detected</p>
          <p className="no-int-sub">The selected medicines have no known interactions in our database.</p>
        </div>
      </motion.div>
    );
  }

  const highCount = interactions.filter(i => i.severity === 'High').length;
  const medCount = interactions.filter(i => i.severity === 'Medium').length;

  return (
    <div className="interaction-section">
      <div className="interaction-summary">
        <span className="int-summary-icon">⚠</span>
        <div className="int-summary-text">
          <strong>{interactions.length} Drug Interaction{interactions.length > 1 ? 's' : ''} Found</strong>
          <span className="int-summary-sub">
            {highCount > 0 && <span className="int-count-badge high">{highCount} High</span>}
            {medCount > 0 && <span className="int-count-badge medium">{medCount} Medium</span>}
          </span>
        </div>
      </div>

      <div className="interactions-list">
        {interactions.map((inter, i) => {
          const Icon = SEVERITY_ICONS[inter.severity] || Info;
          return (
            <motion.div
              key={`${inter.drug_a}-${inter.drug_b}`}
              className={`interaction-item sev-${inter.severity.toLowerCase()}`}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <div className={`int-icon-wrap sev-icon-${inter.severity.toLowerCase()}`}>
                <Icon size={16} />
              </div>

              <div className="int-content">
                <div className="int-drug-pair">
                  <span className="int-drug-name">{inter.drug_a}</span>
                  <span className="int-plus">+</span>
                  <span className="int-drug-name">{inter.drug_b}</span>
                  <span className={`int-severity-badge badge badge-${inter.severity.toLowerCase()}`}>
                    {inter.severity}
                  </span>
                </div>
                <p className="int-description">{inter.description}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
