import { API_BASE_URL } from './config';
// Fetch AI generated sessions and advice (GET /ai/get)
export async function fetchAnalysis() {
  const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE_URL}/ai/get`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch analysis');
  return await res.json();
}

// Generate new AI sessions and advice (POST /ai/generate)
export async function generateAnalysis() {
  const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE_URL}/ai/generate`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to generate analysis');
  return await res.json();
}


// Fetch current user profile (GET /profile/me)
export async function fetchProfile() {
  const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE_URL}/profile/me`, {
    method: 'GET',
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
  const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE_URL}/profile/update`, {
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
  const url = `${API_BASE_URL}/trainsession/${session_id}`;
  const headers: Record<string, string> = {};
  const token = localStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error('Failed to fetch session detail');
  return await res.json();
}


// Fetch train schedules (GET /trainsession/fetch-schedules)
export async function fetchSchedules(token: string, date?: number, etag?: string) {
  const url = new URL(`${API_BASE_URL}/trainsession/fetch-schedules`);
  if (date) url.searchParams.append('date', date.toString());

  // header 
  const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
  if (etag) headers["If-None-Match"] = etag;

  const res = await fetch(url.toString(), {headers});

  // 
  if (res.status == 304) {
    return { notModified: true};
  }

  if (!res.ok) {
    // console.log(res);
    throw new Error('Failed to fetch schedules')
  };
  // 서버에서 새로운 etag + data 내려줌
  const data = await res.json();
  return { notModified: false, ...data };
}

// Fetch new schedules (GET /trainsession/fetch-new-schedules)
export async function fetchNewSchedules(token: string, date?: number) {
  const url = new URL(`${API_BASE_URL}/trainsession/fetch-new-schedules`);
  if (date) url.searchParams.append('date', date.toString());
    const res = await fetch(url.toString(), {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (res.status == 404) throw new Error("no connected party");
  else if (!res.ok) throw new Error('Failed to fetch new schedules');
  return await res.json();
}

// Upload new train session (POST /trainsession/upload)
export async function postNewSchedule(data: {
  train_date: string; // datetime string (ISO or 'YYYY-MM-DD HH:mm:ss.ssssss')
  distance?: number;
  avg_speed?: number;
  total_time?: number;
  activity_title?: string;
  analysis_result?: string;
}) {
  const token = localStorage.getItem('access_token');
  // Ensure train_date is a valid datetime string
  // If needed, convert JS Date to ISO string: new Date().toISOString()
  const res = await fetch(`${API_BASE_URL}/trainsession/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to upload new schedule');
  return await res.json();
}

export async function loginWithEmail(email: string, pwd: string) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ email, pwd }),
     credentials: "include",
  });
  if (!res.ok) throw new Error('Login failed');
  return await res.json();
}

export async function loginWithToken() {
  const accessToken = localStorage.getItem("access_token");
  if (!accessToken) throw new Error('no token');

  const res = await fetch(`${API_BASE_URL}/auth/token`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  });
  if (res.ok) return await res.json();
  
  else { // refresh token
    const device_id = localStorage.getItem("device_id");
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      credentials: "include",
      headers: {
        'Authorization': `Bearer ${device_id}`,
        'Content-Type': 'application/json',
      },
    });
    if (res.ok) return await res.json();
    else throw new Error("no token login");
  }
}

export async function loginWithGoogle() {
  // Get Google login URL from backend
  window.location.href = `${API_BASE_URL}/auth/google/login`;

}

export async function signup(email: string, pwd: string, name: string) {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ email, pwd, name })
  });
  return res.ok;
}


export async function logout(deviceId: string) {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    credentials: 'include', // HttpOnly refresh_token 쿠키 전송
    body: JSON.stringify({ device_id: deviceId }),
  });

  if (!res.ok) {
    throw new Error('Logout failed');
  }
  return await res.json();
}


export async function connectStrava() {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${API_BASE_URL}/auth/strava/connect`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Strava connect failed');
  const { url } = await res.json();
  window.location.href = url;
}
