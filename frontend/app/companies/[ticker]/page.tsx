import {CompanyPage} from '@/components/CompanyPage';
export default async function Page({params}:{params:Promise<{ticker:string}>}){const {ticker}=await params;return <CompanyPage ticker={ticker}/>}
