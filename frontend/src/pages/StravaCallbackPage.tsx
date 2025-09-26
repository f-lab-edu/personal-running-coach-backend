// src/pages/Callback.tsx
import { useEffect } from "react";
import { API_BASE_URL } from '../config';
import { useNavigate } from "react-router-dom";

export default function StravaCallback(
  {setThirdList}: {
    setThirdList: React.Dispatch<React.SetStateAction<string[]>>;
  }) {
  const navigate = useNavigate();

  useEffect(() => {
    const fetchToken = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      if (!code) {
        alert("Google login failed: code missing");
        return;
      }

      const token = localStorage.getItem("access_token");
      if (!token) {
        alert("No access token found. Please login first.");
        navigate("/connect");
        return;
      }
      try {
        // Call backend with code
  const res = await fetch(`${API_BASE_URL}/auth/strava/callback`,{
          method: 'POST',
          headers: { 'Content-Type': 'application/json',
            'Authorization' : `Bearer ${token}`,
          },
          body: JSON.stringify({ code }),
        }
        );
        const data = await res.json();
        if (data.status != "ok") throw new Error(data.msg);
        else setThirdList(prev=>[...prev, "strava"]);
        


        // Redirect to connect page
        navigate("/connect");
      } catch (err) {
        console.error(err);
        alert(`connection failed ${err}`);
        navigate("/connect");
      }
    };

    fetchToken();
  }, []);

  return <div>연결 중...</div>;
}
