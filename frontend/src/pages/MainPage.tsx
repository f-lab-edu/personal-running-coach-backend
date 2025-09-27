import React from 'react';

const MainPage: React.FC<{ user: any, thirdList:string[] }> = ({ user, thirdList }) => {
    const token = localStorage.getItem("access_token");
    return (
        <pre>
            <h2>Main</h2>
            {user && token ? (
                <div>
                    <h3>Login Information:</h3>
                    <pre style={{ background: '#f0f0f0', 
                        padding: '10px', 
                        borderRadius: '5px',
                        width: '100%',
                        maxWidth: '100%',
                        boxSizing: 'border-box',
                        overflowX: 'auto',
                        whiteSpace: 'pre-wrap', // 줄바꿈 허용
                        wordBreak: 'break-word' // 단어 단위로 줄바꿈 
                        }}>
                        Connected: {thirdList}
                        {/* {JSON.stringify({ token, user, thirdList }, null, 2)} */}
                    </pre>
                </div>
            ) : (
                <p>Not logged in.</p>
            )}
        </pre>
        
    );
};

export default MainPage;
