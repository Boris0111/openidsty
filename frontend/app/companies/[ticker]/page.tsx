import {CompanyRedirect} from '@/components/CompanyRedirect';
export default async function Page({params}:{params:Promise<{ticker:string}>}){const {ticker}=await params;return <CompanyRedirect ticker={decodeURIComponent(ticker)}/>}
