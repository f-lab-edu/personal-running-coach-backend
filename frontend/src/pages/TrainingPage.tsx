import React, { useEffect, useState } from 'react';
import { fetchSchedules, fetchNewSchedules } from '../api';
import { calcPace } from '../utils';

interface TrainResponse {
	session_id: string;
	train_date: string;
	distance?: number;
	avg_speed?: number;
	total_time?: number;
	analysis_result?: string;
}

interface TrainingPageProps {
	user: any;
	token: any;
}

// Simple calendar rendering (no external lib)
function getMonthDays(year: number, month: number) {
	const firstDay = new Date(year, month, 1);
	const lastDay = new Date(year, month + 1, 0);
	const days = [];
	for (let d = 1; d <= lastDay.getDate(); d++) {
		days.push(new Date(year, month, d));
	}
	return days;
}

const TrainingPage: React.FC<TrainingPageProps> = ({ user, token }) => {
	const [schedules, setSchedules] = useState<TrainResponse[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');
	const [currentMonth, setCurrentMonth] = useState(() => {
		const now = new Date();
		return new Date(now.getFullYear(), now.getMonth(), 1);
	});

	useEffect(() => {
		if (!token?.access_token) return;
		setLoading(true);
		fetchSchedules(token.access_token)
			.then(data => {
				// console.log(data);
				setSchedules(data);
				})
			.catch(e => setError(e.message))
			.finally(() => setLoading(false));
	}, [token]);

	const handleRefresh = async () => {
		if (!token?.access_token) return;
		setLoading(true);
		setError('');
		try {
			const res = await fetchNewSchedules(token.access_token);
			if (res) {
				const newSchedules = await fetchSchedules(token.access_token);
				setSchedules(newSchedules);
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

	// Map date string (YYYY-MM-DD) to schedule
	const scheduleMap = new Map<string, TrainResponse>();
	schedules.forEach(sch => {
		const key = sch.train_date.slice(0, 10);
		scheduleMap.set(key, sch);
	});

	const todayStr = new Date().toISOString().slice(0, 10);
	// console.log(todayStr);
	return (
		<div>
			<h2>Training Calendar</h2>
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
						const rows = [];
						let cells = [];
						// Empty cells for first week
						for (let i = 0; i < firstWeekday; i++) {
							cells.push(<td key={'empty-' + i}></td>);
						}
						days.forEach((date, idx) => {
							// const key = date.toISOString().slice(0, 10);
							const key = date.toLocaleDateString('sv-SE');
							const sch = scheduleMap.get(key);
							const schKey = sch?.train_date?.slice(0,10);
							const isToday = key === todayStr;
							cells.push(
								<td key={key} style={{
									border: '1px solid #ccc',
									padding: 12,
									minHeight: 80,
									height: '10vh',
									background: isToday ? '#e0f7fa' : schKey === key ? '#ffe0b2' : undefined,
									verticalAlign: 'top',
									width: `${100/7}%`,
								}}>
									<div style={{ fontWeight: isToday ? 'bold' : undefined, fontSize: 20 }}>{date.getDate()}</div>
																{sch && (
																	<div>
																		{/* Title: analysis_result */}
																		<div style={{ fontWeight: 'bold', fontSize: 16, color: '#333', marginBottom: 4 }}>
																			{sch.analysis_result || '훈련'}
																		</div>
																		{/* Details below */}
																		<div style={{ fontSize: 13, color: '#555' }}>
																			{sch.distance !== undefined ? `거리: ${sch.distance}m` : ''}
																			{sch.avg_speed !== undefined ? <><br />평속: {sch.avg_speed.toFixed(2)}</> : null}
																			{sch.total_time !== undefined ? <><br />시간: {sch.total_time}초</> : null}
																			{sch.distance !== undefined && sch.total_time !== undefined ? <><br />페이스: {calcPace(sch.distance, sch.total_time) ?? '-'} min/km</> : null}
																		</div>
																	</div>
																)}
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
