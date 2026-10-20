import type {Metadata} from 'next';
import {SiteFrame} from '@/components/SiteFrame';
import './globals.css';
import './next/research.css';
export const metadata:Metadata={title:{default:'IndustryFlow｜半導體與 AI 產業情報地圖',template:'%s｜IndustryFlow'},description:'從環節與題材理解產業變化，閱讀完整研究、近期事件與資料覆蓋，追溯公開來源。'};
export default function RootLayout({children}:{children:React.ReactNode}) {return <html lang="zh-Hant-TW"><body><a className="skip-link" href="#main">跳到主要內容</a><SiteFrame>{children}</SiteFrame></body></html>}
