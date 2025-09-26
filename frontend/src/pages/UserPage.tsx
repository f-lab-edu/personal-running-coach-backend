
import React, { useEffect, useState } from 'react';
import { fetchProfile, updateProfile } from '../api';

import type { UserInfoData, Profile } from '../types';
// import type { Profile } from '../types';

const UserPage: React.FC = () => {
	const [profile, setProfile] = useState<Profile | null>(null);
	const [edit, setEdit] = useState(false);
	const [form, setForm] = useState<Partial<Profile & { pwd?: string }>>({});
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const infoKeys: (keyof UserInfoData)[] = ['height', 'weight', 'age', 'sex', 'train_goal'];


	useEffect(() => {
		fetchProfile()
			.then(data => {
				setProfile(data);
				setForm({
					name: data.name,
					info: { ...data.info },
				});
			})
			.catch(e => setError(e.message));
	}, []);

	const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
		const { name, value } = e.target;
		console.log(`${name}, ${value}`);
		console.log(profile);
		if (infoKeys.includes(name as keyof UserInfoData)) {
			// 'height' 같은 키는 이 블록으로
			setForm(f => ({
				...f,
				info: {
					...(f.info || {}), // form.info가 혹시라도 null이 되는 경우를 방지
					[name]: value
				}
			}));
		} else {
			// 'name' 같은 키는 이 블록으로 들어옵니다.
			setForm(f => ({ ...f, [name]: value }));
		}
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError(null);
		try {
			const res = await updateProfile({
				name: form.name,
				pwd: form.pwd,
				info: form.info,
			});
			setProfile(res);
			setEdit(false);
		} catch (e: any) {
			setError(e.message);
		} finally {
			setLoading(false);
		}
	};

	if (error) return <div style={{color:'red'}}>Error: {error}</div>;
	if (!profile) return <div>Loading...</div>;

	return (
		<div style={{ maxWidth: 500, margin: '2rem auto', padding: 24, border: '1px solid #ccc', borderRadius: 8 }}>
			<h2>User Profile</h2>
			<div><b>Email:</b> {profile.email}</div>
			<div><b>Provider:</b> {profile.provider}</div>
			{!edit ? (
				<>
					<div><b>Name:</b> {profile.name}</div>
					<div><b>Height:</b> {profile.info?.height ?? '-'}</div>
					<div><b>Weight:</b> {profile.info?.weight ?? '-'}</div>
					<div><b>Age:</b> {profile.info?.age ?? '-'}</div>
					<div><b>Sex:</b> {profile.info?.sex ?? '-'}</div>
					<div><b>Train Goal:</b> {profile.info?.train_goal ?? '-'}</div>
					<button onClick={() => setEdit(true)} style={{marginTop:16}}>Edit</button>
				</>
			) : (
				<form onSubmit={handleSubmit} style={{marginTop:16}}>
					<div>
						<label>Name: <input name="name" value={form.name ?? ''} onChange={handleChange} /></label>
					</div>
					<div>
						<label>Password: <input name="pwd" type="password" value={form.pwd ?? ''} onChange={handleChange} /></label>
					</div>
					<div>
						<label>Height: <input name="height" type="number" value={form.info?.height ?? ''} onChange={handleChange} /></label>
					</div>
					<div>
						<label>Weight: <input name="weight" type="number" value={form.info?.weight ?? ''} onChange={handleChange} /></label>
					</div>
					<div>
						<label>Age: <input name="age" type="number" value={form.info?.age ?? ''} onChange={handleChange} /></label>
					</div>
					<div>
						<label>Sex: <select name="sex" value={form.info?.sex ?? ''} onChange={handleChange}>
							<option value="">-</option>
							<option value="M">M</option>
							<option value="F">F</option>
						</select></label>
					</div>
					<div>
						<label>Train Goal: <input name="train_goal" value={form.info?.train_goal ?? ''} onChange={handleChange} /></label>
					</div>
					<button type="submit" disabled={loading}>{loading ? 'Saving...' : 'Save'}</button>
					<button type="button" onClick={() => setEdit(false)} style={{marginLeft:8}}>Cancel</button>
				</form>
			)}
		</div>
	);
};

export default UserPage;
