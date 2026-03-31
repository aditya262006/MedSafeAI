import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Search, Plus, X, Pill } from 'lucide-react';
import { searchDrugs } from '../api';
import './DrugSearchInput.css';

interface Props {
  selectedDrugs: string[];
  onAdd: (drug: string) => void;
  onRemove: (drug: string) => void;
  isLoading?: boolean;
}

export function DrugSearchInput({ selectedDrugs, onAdd, onRemove, isLoading }: Props) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [focused, setFocused] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) { setSuggestions([]); setIsOpen(false); return; }
    try {
      const data = await searchDrugs(q);
      const filtered = data.suggestions.filter(s => !selectedDrugs.includes(s));
      setSuggestions(filtered);
      setIsOpen(filtered.length > 0);
    } catch {
      setSuggestions([]);
    }
  }, [selectedDrugs]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(query), 250);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query, fetchSuggestions]);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (!dropdownRef.current?.contains(e.target as Node) &&
          !inputRef.current?.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSelect = (drug: string) => {
    if (selectedDrugs.length >= 10) return;
    onAdd(drug);
    setQuery('');
    setSuggestions([]);
    setIsOpen(false);
    setActiveSuggestion(-1);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveSuggestion(i => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveSuggestion(i => Math.max(i - 1, -1));
    } else if (e.key === 'Enter' && activeSuggestion >= 0) {
      e.preventDefault();
      handleSelect(suggestions[activeSuggestion]);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && query.trim() && !isOpen) {
      handleSelect(query.trim().toLowerCase());
    }
    handleKeyDown(e);
  };

  return (
    <div className="drug-search-wrapper">
      <div className={`drug-search-input-box ${focused ? 'focused' : ''}`}>
        <div className="search-icon-wrap">
          <Search size={18} />
        </div>

        <div className="chips-container">
          {selectedDrugs.map(drug => (
            <span key={drug} className="drug-chip">
              <Pill size={12} />
              {drug}
              <button
                className="chip-remove"
                onClick={() => onRemove(drug)}
                aria-label={`Remove ${drug}`}
              >
                <X size={11} />
              </button>
            </span>
          ))}

          <input
            ref={inputRef}
            id="drug-search-input"
            className="drug-text-input"
            type="text"
            value={query}
            onChange={e => { setQuery(e.target.value); setActiveSuggestion(-1); }}
            onKeyDown={handleInputKeyDown}
            onFocus={() => { setFocused(true); if (suggestions.length > 0) setIsOpen(true); }}
            onBlur={() => setFocused(false)}
            placeholder={selectedDrugs.length === 0 ? 'Search for a medicine (e.g. aspirin, warfarin)...' : 'Add another medicine...'}
            disabled={isLoading || selectedDrugs.length >= 10}
            autoComplete="off"
            spellCheck={false}
          />
        </div>

        {query && (
          <button className="clear-input-btn" onClick={() => { setQuery(''); setSuggestions([]); setIsOpen(false); inputRef.current?.focus(); }}>
            <X size={14} />
          </button>
        )}
      </div>

      {isOpen && suggestions.length > 0 && (
        <div ref={dropdownRef} className="suggestions-dropdown" role="listbox">
          {suggestions.map((s, i) => (
            <button
              key={s}
              role="option"
              aria-selected={i === activeSuggestion}
              className={`suggestion-item ${i === activeSuggestion ? 'active' : ''}`}
              onMouseDown={() => handleSelect(s)}
            >
              <Pill size={14} className="suggestion-icon" />
              <span className="suggestion-name">{highlightMatch(s, query)}</span>
              <Plus size={14} className="suggestion-add" />
            </button>
          ))}
        </div>
      )}

      {selectedDrugs.length > 0 && (
        <p className="drug-count-hint">
          {selectedDrugs.length} medicine{selectedDrugs.length > 1 ? 's' : ''} selected
          {selectedDrugs.length >= 2 && ' — interactions will be checked'}
        </p>
      )}
    </div>
  );
}

function highlightMatch(text: string, query: string): React.ReactNode {
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1 || !query) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark>{text.slice(idx, idx + query.length)}</mark>
      {text.slice(idx + query.length)}
    </>
  );
}
