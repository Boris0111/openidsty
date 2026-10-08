'use client';
export default function ErrorPage({reset}:{reset:()=>void}){return <div className="page-content"><h1>頁面暫時無法載入</h1><p>請重新載入，或從產業地圖繼續探索。</p><button onClick={reset}>重新載入</button></div>}
