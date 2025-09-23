import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // 기본적으로 vite 는 localhost, 127.0.0.1 같은 로컬만 허용
  // num run dev 일 경우 외부 도메인을 허용해줘야 함.
  // build 후 nginx 등을 사용하여 프론트 서버를 띄울 경우 상관없음.
  // server: {
  //   host:'0.0.0.0',
  //   allowedHosts: ['www.coach4runners.me'],
  //   port: 5173
  // }
})
