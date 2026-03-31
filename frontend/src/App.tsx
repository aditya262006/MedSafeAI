import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast, { Toaster } from 'react-hot-toast';
import {
  Shield, AlertTriangle, CheckCircle, Zap,
  ArrowRight, Loader2, RotateCcw, Info, ExternalLink
} from 'lucide-react';
import { DrugSearchInput } from './components/DrugSearchInput';
import { DrugResultCard } from './components/DrugResultCard';
import { RiskGauge } from './components/RiskGauge';
import { InteractionAlert } from './components/InteractionAlert';
import { ShapExplanation } from './components/ShapExplanation';
import { HistoryPanel, type HistoryEntry } from './components/HistoryPanel';
import { predictRisk } from './api';
import type { PredictResponse } from './types';
import './App.css';

const EXAMPLE_COMBOS = [
  { drugs: ['aspirin', 'warfarin'], label: 'Aspirin + Warfarin', risk: 'High' },
  { drugs: ['ibuprofen', 'metformin'], label: 'Ibuprofen + Metformin', risk: 'Medium' },
  { drugs: ['cetirizine'], label: 'Cetirizine', risk: 'Low' },
  { drugs: ['sertraline', 'tramadol'], label: 'Sertraline + Tramadol', risk: 'High' },
];

function App() {
  const [selectedDrugs, setSelectedDrugs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<PredictResponse | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const handleAddDrug = useCallback((drug: string) => {
    setSelectedDrugs(prev => {
      if (prev.includes(drug)) {
        toast.error(`${drug} already added`, { style: toastStyle });
        return prev;
      }
      if (prev.length >= 10) {
        toast.error('Maximum 10 medicines at once', { style: toastStyle });
        return prev;
      }
      return [...prev, drug];
    });
  }, []);

  const handleRemoveDrug = useCallback((drug: string) => {
    setSelectedDrugs(prev => prev.filter(d => d !== drug));
  }, []);

  const handleAnalyze = async () => {
    if (selectedDrugs.length === 0) {
      toast.error('Please add at least one medicine', { style: toastStyle });
      return;
    }
    setIsLoading(true);
    try {
      const result = await predictRisk(selectedDrugs);
      setResponse(result);

      // Save to history
      const entry: HistoryEntry = {
        id: Date.now().toString(),
        drugs: [...selectedDrugs],
        combined_risk: result.combined_risk,
        timestamp: new Date(),
        response: result,
      };
      setHistory(prev => [entry, ...prev.slice(0, 19)]);

      // Scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);

      const riskToast = result.combined_risk === 'High'
        ? toast.error
        : result.combined_risk === 'Medium'
        ? toast
        : toast.success;
      riskToast(`Analysis complete — ${result.combined_risk} risk detected`, { style: toastStyle });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Server error — is the backend running?';
      toast.error(msg, { style: toastStyle, duration: 5000 });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedDrugs([]);
    setResponse(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleExampleClick = (drugs: string[]) => {
    setSelectedDrugs(drugs);
    setResponse(null);
  };

  const handleHistorySelect = (res: PredictResponse, drugs: string[]) => {
    setResponse(res);
    setSelectedDrugs(drugs);
    setTimeout(() => {
      document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const combined = response?.combined_risk;

  return (
    <div className="app">
      <div className="app-bg" />
      <Toaster position="top-right" />

      {/* ── HEADER ─────────────────────────────────────────── */}
      <header className="app-header">
        <div className="container header-inner">
          <div className="header-brand">
            <div className="header-logo">
              <Shield size={22} />
            </div>
            <span className="header-title">MedSafe AI</span>
            <span className="header-version">v1.0</span>
          </div>
          <div className="header-right">
            <HistoryPanel
              history={history}
              onSelect={handleHistorySelect}
              onClear={() => setHistory([])}
            />
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary header-api-btn"
            >
              <ExternalLink size={14} />
              API Docs
            </a>
          </div>
        </div>
      </header>

      {/* ── HERO ───────────────────────────────────────────── */}
      <section className="hero-section">
        <div className="container hero-inner">
          <motion.div
            className="hero-content"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            <div className="hero-badge">
              <Zap size={12} />
              AI-Powered Drug Safety Analysis
            </div>

            <h1 className="hero-title">
              Check Medicine
              <br />
              <span className="gradient-text">Side Effects & Risks</span>
            </h1>

            <p className="hero-subtitle">
              Enter one or more medicines to instantly get AI-predicted risk levels,
              drug interaction warnings, and explainable ML insights powered by XGBoost + SHAP.
            </p>

            {/* Search Box */}
            <div className="search-section">
              <DrugSearchInput
                selectedDrugs={selectedDrugs}
                onAdd={handleAddDrug}
                onRemove={handleRemoveDrug}
                isLoading={isLoading}
              />

              <div className="search-actions">
                <button
                  id="analyze-btn"
                  className="btn btn-primary analyze-btn"
                  onClick={handleAnalyze}
                  disabled={isLoading || selectedDrugs.length === 0}
                >
                  {isLoading ? (
                    <><Loader2 size={16} className="spin" /> Analyzing...</>
                  ) : (
                    <>Analyze Risk <ArrowRight size={16} /></>
                  )}
                </button>

                {(selectedDrugs.length > 0 || response) && (
                  <button className="btn btn-secondary reset-btn" onClick={handleReset}>
                    <RotateCcw size={14} />
                    Reset
                  </button>
                )}
              </div>
            </div>

            {/* Example combos */}
            <div className="examples-row">
              <span className="examples-label">Try:</span>
              {EXAMPLE_COMBOS.map(ex => (
                <button
                  key={ex.label}
                  className={`example-pill risk-pill-${ex.risk.toLowerCase()}`}
                  onClick={() => handleExampleClick(ex.drugs)}
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Hero Stats */}
          <motion.div
            className="hero-stats"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            {[
              { value: '149+', label: 'Medicines', icon: '💊' },
              { value: '51', label: 'Interactions', icon: '⚠️' },
              { value: '98%', label: 'ML Accuracy', icon: '🎯' },
              { value: 'SHAP', label: 'Explainable AI', icon: '🧠' },
            ].map(stat => (
              <div key={stat.label} className="hero-stat">
                <span className="hero-stat-icon">{stat.icon}</span>
                <span className="hero-stat-value">{stat.value}</span>
                <span className="hero-stat-label">{stat.label}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── RESULTS ───────────────────────────────────────── */}
      <AnimatePresence>
        {response && (
          <motion.section
            id="results-section"
            className="results-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="container">

              {/* Combined Risk Banner */}
              <motion.div
                className={`combined-risk-banner risk-banner-${combined?.toLowerCase()}`}
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="crb-gauge">
                  <RiskGauge
                    risk={combined as any}
                    score={Math.max(...response.results.map(r => r.risk_score))}
                    size="lg"
                  />
                </div>
                <div className="crb-info">
                  <div className="crb-top">
                    {combined === 'High' && <AlertTriangle size={20} color="var(--risk-high)" />}
                    {combined === 'Medium' && <Info size={20} color="var(--risk-medium)" />}
                    {combined === 'Low' && <CheckCircle size={20} color="var(--risk-low)" />}
                    <h2 className={`crb-risk-label risk-color-${combined?.toLowerCase()}`}>
                      Overall {combined} Risk
                    </h2>
                  </div>
                  <p className="crb-summary" dangerouslySetInnerHTML={{
                    __html: response.summary.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  }} />
                  {response.interactions.length > 0 && (
                    <span className="crb-interaction-warn">
                      <AlertTriangle size={13} />
                      {response.interactions.length} interaction{response.interactions.length > 1 ? 's' : ''} detected — see below
                    </span>
                  )}
                </div>
              </motion.div>

              {/* Results grid */}
              <div className="results-grid">

                {/* Left column: Drug cards */}
                <div className="results-left">
                  <h2 className="section-heading">Drug Analysis</h2>
                  <div className="drug-cards-list">
                    {response.results.map((result, i) => (
                      <DrugResultCard key={result.drug} result={result} index={i} />
                    ))}
                  </div>

                  {/* Interactions */}
                  {response.results.length >= 2 && (
                    <div className="interactions-section">
                      <h2 className="section-heading">Drug Interactions</h2>
                      <InteractionAlert interactions={response.interactions} />
                    </div>
                  )}
                </div>

                {/* Right column: AI Explanation */}
                <div className="results-right">
                  <h2 className="section-heading">AI Explanation</h2>
                  <ShapExplanation results={response.results} />

                  {/* How it works */}
                  <div className="how-it-works">
                    <h3 className="hiw-title">How This Works</h3>
                    <div className="hiw-steps">
                      {[
                        { icon: '🔍', step: 'Input', desc: 'You enter medicine names' },
                        { icon: '📊', step: 'Features', desc: 'Side effects, severity & interactions extracted' },
                        { icon: '🤖', step: 'XGBoost', desc: 'ML model predicts risk class' },
                        { icon: '🧠', step: 'SHAP', desc: 'Explains which factors drove the prediction' },
                      ].map((s, i) => (
                        <div key={s.step} className="hiw-step">
                          <span className="hiw-step-icon">{s.icon}</span>
                          <div>
                            <strong className="hiw-step-name">{s.step}</strong>
                            <p className="hiw-step-desc">{s.desc}</p>
                          </div>
                          {i < 3 && <ArrowRight size={14} className="hiw-arrow" />}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* ── DISCLAIMER FOOTER ─────────────────────────────── */}
      <footer className="app-footer">
        <div className="container footer-inner">
          <div className="disclaimer-box">
            <Info size={14} />
            <p>
              <strong>Disclaimer:</strong> This tool is for educational purposes only and is{' '}
              <strong>not a substitute for professional medical advice</strong>. Always consult a
              qualified healthcare provider before making any medical decisions. Drug interaction
              data is based on publicly available medical literature and may not be exhaustive.
            </p>
          </div>
          <div className="footer-meta">
            <span>MedSafe AI — Hackathon Project</span>
            <span>·</span>
            <span>Dataset: OpenFDA + SIDER (Public Domain)</span>
            <span>·</span>
            <span>Model: XGBoost + SHAP</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

const toastStyle = {
  background: 'var(--bg-card)',
  color: 'var(--text-primary)',
  border: '1px solid var(--border-default)',
  borderRadius: '12px',
  fontFamily: 'Inter, sans-serif',
  fontSize: '14px',
};

export default App;
