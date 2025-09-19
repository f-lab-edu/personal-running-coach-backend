import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup } from '../api';

const SignupPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [pwd, setPwd] = useState('');
  const [name, setName] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await signup(email, pwd, name);
      setResult(res ? 'Signup successful' : 'Signup failed');
      setTimeout(() => navigate('/login'), 1200);
    } catch {
      setResult('Signup failed');
    }
  };

  return (
    <div>
      <h2>Signup</h2>
      <form onSubmit={handleSignup}>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={pwd} onChange={e => setPwd(e.target.value)} required />
        <input type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
        <button type="submit">Signup</button>
      </form>
      {result && <div>{result}</div>}
    </div>
  );
};
export default SignupPage;
