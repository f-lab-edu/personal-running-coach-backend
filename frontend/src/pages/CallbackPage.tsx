// src/pages/Callback.tsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function CallbackPage(
  {setUser, setToken, setThirdList}: {
    setUser: (user: any) => void;
  setToken: (token: any) => void;
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
        const res = await fetch(`http://localhost:8000/auth/google/callback`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ code }),
        });
        if (!res.ok) throw new Error("Login failed");
        const data = await res.json();

        // Save token and user info
        sessionStorage.setItem("access_token", data.token.access_token);
        sessionStorage.setItem("refresh_token", data.token.refresh_token);
        // 부모 state 업데이트
        setUser(data.user);
        setToken(data.token);
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
