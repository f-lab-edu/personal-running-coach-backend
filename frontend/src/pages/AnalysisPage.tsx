import React, { useEffect, useState } from 'react';
import { fetchAnalysis, generateAnalysis } from '../api';
import type { LLMResponse, LLMSessionResult } from '../types';

const AnalysisPage: React.FC = () => {
  const [data, setData] = useState<LLMResponse | null | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAnalysis();
      setData(res && (res.sessions || res.advice) ? res : null);
    } catch (e: any) {
      setError(e.message || 'Failed to load analysis');
      // Do NOT clear previous data
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalysis();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const res = await generateAnalysis();
      if (!res || (!res.sessions && !res.advice)) {
        setError('You are not authorized to generate analysis yet.');
        // Do NOT clear previous data
      } else {
        setData(res);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to generate analysis');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <h2>Analysis</h2>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
        <button onClick={handleGenerate} disabled={generating}>
          {generating ? 'Generating...' : 'Generate'}
        </button>
        {error && (
          <span style={{ color: 'red', marginLeft: 16 }}>{error}</span>
        )}
      </div>
      {loading ? (
        <div>Loading...</div>
      ) : !data ? (
        <div>No data</div>
      ) : (
        <div style={{display: 'flex', gap: 40}}>
          {/* Sessions Section */}
          <div style={{flex: 1}}>
            <h3>AI Generated Sessions</h3>
            {data.sessions && data.sessions.length > 0 ? (
              <table style={{width: '100%', borderCollapse: 'collapse'}}>
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Workout Type</th>
                    <th>Distance (km)</th>
                    <th>Pace</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {data.sessions.map((s: LLMSessionResult, idx: number) => (
                    <tr key={idx}>
                      <td>{s.day}</td>
                      <td>{s.workout_type}</td>
                      <td>{s.distance_km}</td>
                      <td>{s.pace || '-'}</td>
                      <td>{s.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div>No sessions generated</div>
            )}
          </div>
          {/* Advice Section */}
          <div style={{flex: 1}}>
            <h3>Coach Advice</h3>
            {data.advice ? (
              <div style={{background: '#f9f9f9', padding: 16, borderRadius: 8}}>{data.advice}</div>
            ) : (
              <div>No advice generated</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage;
