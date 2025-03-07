/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}', // 让 Tailwind 处理所有 React 组件
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}


