import {Suspense} from 'react';
import {CompanyByTicker} from '@/components/CompanyRedirect';
export default function Page(){return <Suspense fallback={<div className="page-content"><p role="status">正在開啟公司研究…</p></div>}><CompanyByTicker/></Suspense>}
