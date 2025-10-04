import React, { useEffect, useState } from 'react';
import { fetchSchedules, fetchNewSchedules } from '../api';
import { useNavigate } from 'react-router-dom';

import type { TrainResponse } from '../types';

// Simple calendar rendering (no external lib)
function getMonthDays(year: number, month: number) {
	const lastDay = new Date(year, month + 1, 0);
	const days = [];
	for (let d = 1; d <= lastDay.getDate(); d++) {
		days.push(new Date(year, month, d));
	}
	return days;
}

// const TrainingPage: React.FC<TrainingPageProps> = ({ token }) => {
const TrainingPage: React.FC = () => {
	const [schedules, setSchedules] = useState<TrainResponse[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');
	const [currentMonth, setCurrentMonth] = useState(() => {
		const now = new Date();
		return new Date(now.getFullYear(), now.getMonth(), 1);
	});

	const accessToken = localStorage.getItem('access_token');

	// Helper keys for sessionStorage
	const ETAG_KEY = 'train_schedules_etag';
	const DATA_KEY = 'train_schedules_data';

	useEffect(() => {
		if (!accessToken) return;
		setLoading(true);
		setError('');
		// Get etag from sessionStorage
		const etag = sessionStorage.getItem(ETAG_KEY) || undefined;
		fetchSchedules(accessToken, undefined, etag)
			.then(result => {
				if (result.notModified) {
					// Use cached data
					const cached = sessionStorage.getItem(DATA_KEY);
					if (cached) {
						try {
							setSchedules(JSON.parse(cached));
						} catch {
							setSchedules([]);
						}
					} else {
						setSchedules([]);
					}
				} else {
					// Save new etag and data to sessionStorage
					if (result.etag) sessionStorage.setItem(ETAG_KEY, result.etag);
					if (result.data) sessionStorage.setItem(DATA_KEY, JSON.stringify(result.data));
					setSchedules(result.data || []);
				}
			})
			.catch(e => setError(e.message))
			.finally(() => setLoading(false));
	}, [accessToken]);

		const handleRefresh = async () => {
			if (!accessToken) return;
			setLoading(true);
			setError('');
			try {
				const res = await fetchNewSchedules(accessToken);
				if (res) {
					// After new schedules are generated, fetch with etag again
					const etag = sessionStorage.getItem(ETAG_KEY) || undefined;
					const result = await fetchSchedules(accessToken, undefined, etag);
					if (result.notModified) {
						const cached = sessionStorage.getItem(DATA_KEY);
						if (cached) {
							try {
								setSchedules(JSON.parse(cached));
							} catch {
								setSchedules([]);
							}
						} else {
							setSchedules([]);
						}
					} else {
						if (result.etag) sessionStorage.setItem(ETAG_KEY, result.etag);
						if (result.data) sessionStorage.setItem(DATA_KEY, JSON.stringify(result.data));
						setSchedules(result.data || []);
					}
				}
			} catch (e: any) {
				setError(e.message);
			} finally {
				setLoading(false);
			}
		};

	// Calendar logic
	const year = currentMonth.getFullYear();
	const month = currentMonth.getMonth();
	const days = getMonthDays(year, month);
	const firstWeekday = new Date(year, month, 1).getDay();

	// Map date string (YYYY-MM-DD) to array of schedules
	const scheduleMap = new Map<string, TrainResponse[]>();
	schedules.forEach(sch => {
		const key = sch.train_date.slice(0, 10);
		if (!scheduleMap.has(key)) scheduleMap.set(key, []);
		scheduleMap.get(key)!.push(sch);
	});

	const todayStr = new Date().toISOString().slice(0, 10);
	const navigate = useNavigate();
		return (
			<div>
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
					<h2>Training Calendar</h2>
					<button onClick={() => navigate('/training/add')} style={{ padding: '8px 18px', fontSize: 16 }}>Add</button>
				</div>
				<div style={{ marginBottom: 16 }}>
					<button onClick={() => setCurrentMonth(new Date(year, month - 1, 1))}>{'<'}</button>
					<span style={{ margin: '0 12px' }}>{year}년 {month + 1}월</span>
					<button onClick={() => setCurrentMonth(new Date(year, month + 1, 1))}>{'>'}</button>
					<button style={{ marginLeft: 24 }} onClick={handleRefresh} disabled={loading}>Refresh</button>
				</div>
				{error && <div style={{ color: 'red' }}>{error}</div>}
				<div style={{ overflowX: 'auto', width: '100%', height: '70vh', minHeight: 500 }}>
					<table style={{ borderCollapse: 'collapse', width: '100%', minWidth: 600, maxWidth: '100%', height: '100%', tableLayout: 'fixed' }}>
						<thead>
							<tr>
								{['일', '월', '화', '수', '목', '금', '토'].map(d => (
									<th key={d} style={{ border: '1px solid #ccc', padding: 12, fontSize: 18, width: `${100/7}%` }}>{d}</th>
								))}
							</tr>
						</thead>
						<tbody>
							{(() => {
								const rows: React.ReactNode[] = [];
								let cells: React.ReactNode[] = [];
								// Empty cells for first week
								for (let i = 0; i < firstWeekday; i++) {
									cells.push(<td key={'empty-' + i}></td>);
								}
								days.forEach((date, idx) => {
									const key = date.toLocaleDateString('sv-SE');
									const schArr = scheduleMap.get(key);
									const isToday = key === todayStr;
									cells.push(
										<td key={key} style={{
											border: '1px solid #ccc',
											padding: 12,
											minHeight: 80,
											height: '10vh',
											background: isToday ? '#e0f7fa' : schArr ? '#ffe0b2' : undefined,
											verticalAlign: 'top',
											width: `${100/7}%`,
										}}>
											<div style={{ fontWeight: isToday ? 'bold' : undefined, fontSize: 20 }}>{date.getDate()}</div>
											{schArr && schArr.map(sch => (
												<div
													key={sch.session_id}
													style={{
														fontWeight: 'bold',
														fontSize: 16,
														color: '#1976d2',
														marginBottom: 4,
														cursor: 'pointer',
														textDecoration: 'underline',
													}}
													onClick={() => navigate(`/training/${sch.session_id}`, { state: { session: sch } })}
													title={sch.analysis_result || '훈련'}
												>
													{sch.activity_title || '훈련'}
												</div>
											))}
										</td>
									);
									if ((cells.length) % 7 === 0) {
										rows.push(<tr key={'row-' + idx}>{cells}</tr>);
										cells = [];
									}
								});
								if (cells.length) {
									while (cells.length < 7) cells.push(<td key={'empty-end-' + cells.length}></td>);
									rows.push(<tr key={'row-last'}>{cells}</tr>);
								}
								return rows;
							})()}
						</tbody>
					</table>
				</div>
				{loading && <div>Loading...</div>}
			</div>
		);
};

export default TrainingPage;
