import React, { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { fetchTrainDetail } from '../api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Legend,
  Tooltip,
} from 'chart.js';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Legend, Tooltip);

import type { StreamData, TrainDetail } from '../types';

const plotFields: { key: keyof StreamData; label: string; color: string }[] = [
  { key: 'heartrate', label: 'Heart Rate', color: 'red' },
  { key: 'cadence', label: 'Cadence', color: 'blue' },
  { key: 'distance', label: 'Distance', color: 'green' },
  { key: 'velocity', label: 'Velocity', color: 'orange' },
  { key: 'altitude', label: 'Altitude', color: 'purple' },
];

const TrainingDetailPage: React.FC = () => {
  const { session_id } = useParams<{ session_id: string }>();
  const location = useLocation();
  const passedSession = (location.state as any)?.session as Partial<TrainDetail> | undefined;
  const [detail, setDetail] = useState<TrainDetail | null>();
  const [loading, setLoading] = useState(!passedSession);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!session_id) return;
    if (passedSession && passedSession.stream) {
      setLoading(false);
      return;
    }
    setLoading(true);
    fetchTrainDetail(session_id)
      .then(data => setDetail(data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [session_id, passedSession]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!detail) return <div>No data found.</div>;
  const { stream, laps } = detail;

  // Session summary (from passedSession or fetched detail)
  const summary = (
    <div style={{ marginBottom: 24, background: '#f8f8f8', padding: 16, borderRadius: 8 }}>
      <h2>Training Summary</h2>
      <div><b>분석 결과:</b> {passedSession?.analysis_result || '-'}</div>
      <div><b>일자:</b> {passedSession?.train_date}</div>
      <div><b>거리:</b> {passedSession?.distance ?? '-'} m</div>
      <div><b>평균 속도:</b> {passedSession?.avg_speed ?? '-'} m/s</div>
      <div><b>총 시간:</b> {passedSession?.total_time ?? '-'} 초</div>
    </div>
  );

  // Lap data print (if present)
  const lapSection = laps ? (
    <div style={{ marginBottom: 32 }}>
      <h3>Lap Data</h3>
      <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, maxHeight: 300, overflow: 'auto' }}>
        {JSON.stringify(laps, null, 2)}
      </pre>
    </div>
  ) : null;

  // Stream graphs
  const streamSection = stream ? (
    <div style={{ marginTop: 32 }}>
      <h3>Stream Data</h3>
      {plotFields.map(({ key, label, color }) =>
        stream[key] && Array.isArray(stream[key]) && stream[key]!.length > 0 ? (
          <div key={key} style={{ marginBottom: 32 }}>
            <b>{label}</b>
            <Line
              data={{
                labels: stream.time?.slice(0, stream[key]!.length) ?? stream[key]!.map((_, i) => i),
                datasets: [
                  {
                    label,
                    data: stream[key]!,
                    borderColor: color,
                    backgroundColor: color + '33',
                    fill: false,
                    tension: 0.2,
                    pointRadius: 0,
                  },
                ],
              }}
              options={{
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                  x: { title: { display: true, text: stream.time ? 'Time (s)' : 'Index' } },
                  y: { title: { display: true, text: label } },
                },
              }}
              height={120}
            />
          </div>
        ) : null
      )}
    </div>
  ) : null;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
      {summary}
      {lapSection}
      {streamSection}
    </div>
  );
};

export default TrainingDetailPage;
