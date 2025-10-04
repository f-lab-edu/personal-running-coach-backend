import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginWithEmail, loginWithGoogle } from '../api';

const LoginPage: React.FC<
{ setUser: (user: any) => void, 
  setThirdList: React.Dispatch<React.SetStateAction<string[]>>;
}> = ({ setUser, setThirdList }) => {
  const [email, setEmail] = useState('');
  const [pwd, setPwd] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await loginWithEmail(email, pwd);
      console.log(res)
      setUser(res.user);
      setThirdList(res.connected);
      localStorage.setItem('access_token', res.token.access_token);
      localStorage.setItem("device_id", res.device_id)
      // localStorage.setItem('refresh_token', res.token.refresh_token);
      navigate('/');
    } catch (err: any) {
      setError('Login failed');
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle();
    } catch (err) {
      setError('Google login failed');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={pwd} onChange={e => setPwd(e.target.value)} required />
        <button type="submit">Login</button>
      </form>
      <button onClick={handleGoogleLogin}>Login with Google</button>
      <button onClick={() => navigate('/signup')}>Signup</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
};
export default LoginPage;
