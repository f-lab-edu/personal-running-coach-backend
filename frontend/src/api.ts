const BASE_URL = 'http://localhost:8000';

// Fetch current user profile (GET /profile/me)
export async function fetchProfile() {
  const token = sessionStorage.getItem('access_token');
  const res = await fetch(`${BASE_URL}/profile/me`, {
    method: 'PUT',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch profile');
  return await res.json();
}

// Update user profile (PUT /profile/update)
export async function updateProfile(data: {
  name?: string;
  pwd?: string;
  provider?: string;
  info?: {
    height?: number;
    weight?: number;
    age?: number;
    sex?: string;
    train_goal?: string;
  };
}) {
  const token = sessionStorage.getItem('access_token');
  const res = await fetch(`${BASE_URL}/profile/update`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to update profile');
  return await res.json();
}


// Fetch train session detail (GET /trainsession/{session_id})
export async function fetchTrainDetail(session_id: string) {
  const url = `${BASE_URL}/trainsession/${session_id}`;
  const headers: Record<string, string> = {};
  const token = sessionStorage.getItem('access_token');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error('Failed to fetch session detail');
  return await res.json();
}


// Fetch train schedules (GET /trainsession/fetch-schedules)
export async function fetchSchedules(token: string, date?: number) {
  const url = new URL(`${BASE_URL}/trainsession/fetch-schedules`);
  if (date) url.searchParams.append('date', date.toString());
  const res = await fetch(url.toString(), {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch schedules');
  return await res.json();
}

// Fetch new schedules (GET /trainsession/fetch-new-schedules)
export async function fetchNewSchedules(token: string, date?: number) {
  const url = new URL(`${BASE_URL}/trainsession/fetch-new-schedules`);
  if (date) url.searchParams.append('date', date.toString());
  const res = await fetch(url.toString(), {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch new schedules');
  return await res.json();
}

export async function loginWithEmail(email: string, pwd: string) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, pwd })
  });
  if (!res.ok) throw new Error('Login failed');
  return await res.json();
}

export async function loginWithGoogle() {
  // Get Google login URL from backend
  window.location.href = `${BASE_URL}/auth/google/login`;

}

export async function signup(email: string, pwd: string, name: string) {
  const res = await fetch(`${BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, pwd, name })
  });
  return res.ok;
}

export async function connectStrava() {
  const token = sessionStorage.getItem('access_token');
  const res = await fetch(`${BASE_URL}/auth/strava/connect`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Strava connect failed');
  const { url } = await res.json();
  window.location.href = url;
}
