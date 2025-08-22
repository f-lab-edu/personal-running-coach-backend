backend base is localhost:8000
each page can be navigated from left nav bar.
top bar has login status

each page files should be saved under pages folder. 

1. main page ("/") = just empty. just write some words "main"
2. login page. ("/login") = typical login page. will have normal email/pwd login, google login button, and signup button
    - normal login => call /auth/login
    - google login call /auth/google/login . it will redirect to google login page, and after login, it will go to callback. 
            -> at /auth/google/callback 
    - return value when logged in
    {
    "token":{"access_token":"...",
                "refresh_token":""},
    "user":{"id":"...","email":"...","name":"...","provider":"..."}
    }

    - when logged in, navigate back to main. responses and tokens are saved, login status is shown on the top bar (show name with logout button. ) 

3. signup page ("/signup") just needs email, pwd, name => call /auth/signup. 
    - show result (boolean) and navigate back to login page.

4. connect page. controls third party connection. at this moment, just one selection strava.
    - strava icon. connect button on the bottom of icon. when clicked, call /auth/strava/connect. should include access token in the header.
    - /connect will return. retrieve url and navigate to url.
            class RedirectResponse(
            url: str | URL,
            status_code: int = 307,
            headers: Mapping[str, str] | None = None,
            background: BackgroundTask | None = None
        )
    - when user logs in with strava id, it will direct back to /auth/strava/callback. and will return  {"status": "ok" / "fail", "message": msg}
    - if its connected successfully, update the connect button to connected.


