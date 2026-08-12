import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, ChevronRight, X, Clock, Pill } from 'lucide-react';
import type { PredictResponse } from '../types';
import './HistoryPanel.css';

export interface HistoryEntry {
  id: string;
  drugs: string[];
  combined_risk: string;
  timestamp: Date;
  response: PredictResponse;
}

interface Props {
  history: HistoryEntry[];
  onSelect: (response: PredictResponse, drugs: string[]) => void;
  onClear: () => void;
}

export function HistoryPanel({ history, onSelect, onClear }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Sticky Sidebar Toggle */}
      <button
        className={`history-sidebar-toggle ${open ? 'hidden' : ''}`}
        onClick={() => setOpen(true)}
        aria-label="View history"
      >
        <History size={20} />
        {history.length > 0 && (
          <span className="history-badge-pulse">{history.length}</span>
        )}
      </button>

      {/* Slide-out panel from left */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              className="history-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
            />
            <motion.div
              className="history-panel left-side"
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 32 }}
            >
              <div className="history-panel-header">
                <div className="history-panel-title">
                  <History size={18} />
                  <span>Search History</span>
                </div>
                <div className="history-panel-actions">
                  {history.length > 0 && (
                    <button className="btn btn-secondary history-clear-btn" onClick={onClear}>
                      Clear All
                    </button>
                  )}
                  <button className="history-close-btn" onClick={() => setOpen(false)}>
                    <X size={18} />
                  </button>
                </div>
              </div>

              <div className="history-list">
                {history.length === 0 ? (
                  <div className="history-empty">
                    <History size={32} />
                    <p>No recent searches</p>
                  </div>
                ) : (
                  history.map((entry, i) => (
                    <motion.button
                      key={entry.id}
                      className="history-entry"
                      onClick={() => { onSelect(entry.response, entry.drugs); setOpen(false); }}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      whileHover={{ x: 2 }}
                    >
                      <div className="history-entry-drugs">
                        {entry.drugs.map(d => (
                          <span key={d} className="history-drug-chip">
                            <Pill size={10} />
                            {d}
                          </span>
                        ))}
                      </div>
                      <div className="history-entry-meta">
                        <span className={`history-risk-badge risk-${entry.combined_risk.toLowerCase()}`}>
                          {entry.combined_risk} Risk
                        </span>
                        <span className="history-time">
                          <Clock size={11} />
                          {formatTime(entry.timestamp)}
                        </span>
                      </div>
                      <ChevronRight size={14} className="history-entry-arrow" />
                    </motion.button>
                  ))
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = (now.getTime() - date.getTime()) / 1000;
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
