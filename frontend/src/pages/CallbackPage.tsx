// src/pages/Callback.tsx
import { useEffect } from "react";
import { API_BASE_URL } from '../config';
import { useNavigate } from "react-router-dom";

export default function CallbackPage(
  {setUser, setThirdList}: {
    setUser: (user: any) => void;
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

      try {
        // Call backend with code
  const res = await fetch(`${API_BASE_URL}/auth/google/callback`, {
          method: "POST",
          credentials:"include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ code }),
        });
        if (!res.ok) throw new Error("Login failed");
        const data = await res.json();

        // Save token, device_id, user info
        localStorage.setItem("access_token", data.token.access_token);
        localStorage.setItem("device_id", data.device_id)
        // 부모 state 업데이트
        setUser(data.user);
        setThirdList(data.connected);

        // Redirect to main page
        navigate("/");
      } catch (err) {
        console.error(err);
        alert(`Login failed ${err}`);
        navigate("/login");
      }
    };

    fetchToken();
  }, []);

  return <div>로그인 중...</div>;
}
