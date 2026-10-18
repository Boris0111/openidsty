import {Suspense} from 'react';
import {ResearchExplorer} from '@/components/ResearchExplorer';
import {ResearchWatchlistProvider} from '@/lib/research-watchlist';
import './research.css';
export const metadata={title:'液冷產品與公司研究'};
export default function ResearchPreview(){return <ResearchWatchlistProvider><Suspense fallback={<p>正在讀取研究…</p>}><ResearchExplorer/></Suspense></ResearchWatchlistProvider>}
