import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, AlertTriangle, ArrowRight } from 'lucide-react';
import { searchBySymptom } from '../api';
import type { SymptomResult } from '../types';
import './SymptomSearch.css';

interface Props {
  onSelectDrug: (drug: string) => void;
}

const COMMON_SYMPTOMS = ['headache', 'fever', 'allergies', 'pain', 'anxiety', 'cough', 'nausea'];

export function DrugIcon({ drugName, size = 24 }: { drugName: string, size?: number }) {
  let hash = 0;
  for (let i = 0; i < drugName.length; i++) {
    hash = drugName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash % 360);
  const color1 = `hsl(${hue}, 80%, 65%)`;
  const color2 = `hsl(${(hue + 40) % 360}, 80%, 55%)`;

  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="8" width="18" height="8" rx="4" fill={`url(#grad-${drugName})`} />
      <path d="M12 8V16" stroke="white" strokeWidth="2" strokeLinecap="round" />
      <defs>
        <linearGradient id={`grad-${drugName}`} x1="3" y1="8" x2="21" y2="16" gradientUnits="userSpaceOnUse">
          <stop stopColor={color1} />
          <stop offset="1" stopColor={color2} />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function SymptomSearch({ onSelectDrug }: Props) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SymptomResult | null>(null);
  const [error, setError] = useState('');

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim() || searchQuery.length < 2) return;
    
    setQuery(searchQuery);
    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await searchBySymptom(searchQuery);
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'No medications found for this symptom.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="symptom-search-container">
      <div className="symptom-search-input-wrap">
        <Search className="symptom-search-icon" size={20} />
        <input
          type="text"
          className="symptom-search-input"
          placeholder="e.g. headache, fever, allergies..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch(query)}
        />
        <button 
          className="btn btn-primary symptom-search-btn"
          onClick={() => handleSearch(query)}
          disabled={isLoading || query.length < 2}
        >
          {isLoading ? <Loader2 size={16} className="spin" /> : 'Search'}
        </button>
      </div>

      <div className="symptom-quick-chips">
        <span className="symptom-quick-label">Try:</span>
        {COMMON_SYMPTOMS.map(s => (
          <button 
            key={s} 
            className="symptom-chip"
            onClick={() => handleSearch(s)}
          >
            {s}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {error && (
          <motion.div 
            key="error"
            className="symptom-error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <AlertTriangle size={16} />
            {error}
          </motion.div>
        )}

        {result && (
          <motion.div 
            key="result"
            className="symptom-result-card glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="symptom-result-header">
              <h3>Recommended for: <span className="highlight-symptom">{result.symptom || query}</span></h3>
              <span className={`symptom-severity-badge sev-${result.severity}`}>
                {result.severity} severity
              </span>
            </div>

            <p className="symptom-advice">{result.advice}</p>

            {result.consult_doctor && (
              <div className="symptom-consult-warn">
                <AlertTriangle size={16} />
                <strong>Consult Doctor:</strong> This condition requires professional medical advice. Do not self-medicate without supervision.
              </div>
            )}

            <div className="symptom-drugs-list">
              <h4>Common Medications</h4>
              <div className="symptom-drugs-grid">
                {result.drugs.map(drug => (
                  <div key={drug} className="symptom-drug-item">
                    <DrugIcon drugName={drug} size={28} />
                    <span className="symptom-drug-name">{drug}</span>
                    <button 
                      className="symptom-add-drug-btn"
                      onClick={() => onSelectDrug(drug)}
                      title="Add to Analyzer"
                    >
                      <ArrowRight size={14} /> Analyze
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
