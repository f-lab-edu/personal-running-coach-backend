const BASE_URL = 'http://localhost:8000';

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
  window.location.href = `${BASE_URL}/auth/strava/connect`
  // const res = await fetch(`${BASE_URL}/auth/strava/connect`, {
  //   headers: { 'Authorization': `Bearer ${token}` }
  // });
  // if (!res.ok) throw new Error('Strava connect failed');
  // const { url } = await res.json();
  // return url;
}
