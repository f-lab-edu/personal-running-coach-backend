import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate} from 'react-router-dom';
import { loginWithToken, logout } from './api.ts';

// Placeholder pages
import MainPage from './pages/MainPage.tsx';
import LoginPage from './pages/LoginPage.tsx';
import SignupPage from './pages/SignupPage.tsx';
import ConnectPage from './pages/ConnectPage.tsx';
import TrainingPage from './pages/TrainingPage.tsx';
import CallbackPage from './pages/CallbackPage.tsx';
import StravaCallback from './pages/StravaCallbackPage.tsx';
import TrainingDetailPage from './pages/TrainingDetailPage';
import UserPage from './pages/UserPage';
import AnalysisPage from './pages/AnalysisPage';
import TrainingAddPage from './pages/TrainingAddPage';

// Top bar component
const TopBar = ({ user, onLogout, onLogin }: { user: any, onLogout: () => void , onLogin: ()=> void}) => (
	<div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', padding: '10px', background: '#eee' }}>
		{user ? (
			<>
				<span style={{ marginRight: '10px' }}>{user.name}</span>
				<button onClick={onLogout}>Logout</button>
			</>
		) : (
			<>
				<button onClick={onLogin}>Log In</button>
			</>
			// <span>Not logged in</span>
		)}
	</div>
);

// Left nav bar component
const LeftNav = () => (
    <nav style={{ width: '180px', background: '#f5f5f5', height: '100vh', padding: '20px 0', boxSizing: 'border-box' }}>
        <ul style={{ listStyle: 'none', padding: 0 }}>
            <li><Link to="/">Main</Link></li>
            <li><Link to="/user">User Profile</Link></li>
            <li><Link to="/signup">Signup</Link></li>
            <li><Link to="/connect">Connect</Link></li>
            <li><Link to="/training">training</Link></li>
            <li><Link to="/analysis">Analysis</Link></li>
        </ul>
    </nav>
);

const App: React.FC = () => {
    const [user, setUser] = useState<any>(null);
    const [thirdList, setThirdList] = useState<string[]>([]);

    const navigate = useNavigate();

    useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
        loginWithToken()
        .then(res => {
            setUser(res.user);
            setThirdList(res.connected);
            if (res.token){
                localStorage.setItem("access_token", res.token.access_token);
            }
        })
        .catch(() => {
            handleLogout()
        });
    }
    }, []);


    const handleLogout = async () => {
        setUser(null);
        setThirdList([]);
        const device_id = localStorage.getItem("device_id") || "";
        await logout(device_id);
        
        localStorage.removeItem("access_token");
        localStorage.removeItem("device_id");
        sessionStorage.clear();

        navigate("/");
    };

    const handleLogin = () => {
        navigate("/login");
        // Optionally clear tokens from storage
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <TopBar user={user} onLogout={handleLogout} onLogin={handleLogin}/>
            <div style={{ display: 'flex', flex: 1 }}>
                <LeftNav />
                <div style={{ flex: 1, padding: '30px' }}>
                    <Routes>
                        <Route path="/" element={<MainPage user={user} thirdList={thirdList}/>} />
                        <Route path="/user" element={<UserPage />} />
                        <Route path="/auth/google/callback" element={<CallbackPage setUser={setUser} 
                                                                                    setThirdList={setThirdList}/>} />
                        <Route path="/auth/strava/callback" element={<StravaCallback setThirdList={setThirdList}/>} />
                        <Route path="/login" element={<LoginPage setUser={setUser} 
                                                                setThirdList={setThirdList}/>} />
                        <Route path="/signup" element={<SignupPage />} />
                        <Route path="/connect" element={<ConnectPage thirdList={thirdList}/>} />
                        <Route path="/training" element={<TrainingPage />} />
                        <Route path="/training/add" element={<TrainingAddPage user={user} />} />
                        <Route path="/training/:session_id" element={<TrainingDetailPage />} />
                        <Route path="/analysis" element={<AnalysisPage />} />
                    </Routes>
                </div>
            </div>
        </div>
    );
};

export default App;
