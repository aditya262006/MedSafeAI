import { motion } from 'framer-motion';
import type { RiskLevel } from '../types';
import './RiskGauge.css';

interface Props {
  risk: RiskLevel;
  score: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

const RISK_CONFIG = {
  Low:    { color: '#00C896', glow: 'rgba(0,200,150,0.3)',    angle: 60,  label: 'Low Risk',    emoji: '✓' },
  Medium: { color: '#FFB830', glow: 'rgba(255,184,48,0.3)',   angle: 170, label: 'Medium Risk',  emoji: '!' },
  High:   { color: '#FF4757', glow: 'rgba(255,71,87,0.3)',    angle: 280, label: 'High Risk',    emoji: '⚠' },
};

export function RiskGauge({ risk, score, label, size = 'md' }: Props) {
  const cfg = RISK_CONFIG[risk];
  const radius = size === 'lg' ? 70 : size === 'sm' ? 40 : 55;
  const stroke = size === 'lg' ? 8 : size === 'sm' ? 5 : 6;
  const cx = radius + stroke + 4;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (score * circumference);

  return (
    <div className={`risk-gauge-wrap risk-gauge-${size} risk-${risk.toLowerCase()}`}>
      <div className="gauge-svg-wrap">
        <svg
          width={cx * 2}
          height={cx * 2}
          viewBox={`0 0 ${cx * 2} ${cx * 2}`}
          className="gauge-svg"
        >
          {/* Glow filter */}
          <defs>
            <filter id={`glow-${risk}`} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Background track */}
          <circle
            cx={cx}
            cy={cx}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={stroke}
          />

          {/* Animated progress arc */}
          <motion.circle
            cx={cx}
            cy={cx}
            r={radius}
            fill="none"
            stroke={cfg.color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 1.2, ease: 'easeOut', delay: 0.2 }}
            style={{ transformOrigin: `${cx}px ${cx}px`, transform: 'rotate(-90deg)' }}
            filter={`url(#glow-${risk})`}
          />
        </svg>

        {/* Center content */}
        <div className="gauge-center">
          <motion.span
            className="gauge-emoji"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: 'spring', stiffness: 300 }}
            style={{ color: cfg.color }}
          >
            {cfg.emoji}
          </motion.span>
          <span className="gauge-pct" style={{ color: cfg.color }}>
            {Math.round(score * 100)}%
          </span>
        </div>
      </div>

      <motion.div
        className="gauge-label"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <span className={`gauge-risk-text risk-color-${risk.toLowerCase()}`}>{cfg.label}</span>
        {label && <span className="gauge-drug-label">{label}</span>}
      </motion.div>
    </div>
  );
}
