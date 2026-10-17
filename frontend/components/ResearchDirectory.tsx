'use client';
import Link from 'next/link';
import {useRouter,useSearchParams} from 'next/navigation';
import {useResearch,ResearchPage} from '@/lib/research-api';

export const directoryNames={segments:'產業環節',applications:'應用',roles:'供應角色',products:'產品',companies:'公司',themes:'題材',concepts:'術語'};
export type DirectoryView=keyof typeof directoryNames;
export function directoryView(value:string|null):DirectoryView|null{return value&&Object.hasOwn(directoryNames,value)?value as DirectoryView:null}
type IndexHref=(view:DirectoryView,filters?:Record<string,string>)=>string;

export function ResearchDirectory({view,release,href,indexHref}:{view:DirectoryView;release:string;href:(id:string)=>string;indexHref:IndexHref}){
  const params=useSearchParams(),router=useRouter();
  const market=view==='companies'?params.get('market')||'':'';
  const role=view==='companies'?params.get('role')||'':'';
  const category=['companies','products','roles'].includes(view)?params.get('category')||'':'';
  const cursor=params.get('cursor')||'';
  const filters={market,role,category};
  const query=new URLSearchParams({release_id:release});
  for(const [key,value] of Object.entries({...filters,cursor}))if(value)query.set(key,value);
  const result=useResearch<ResearchPage>(`/api/v2/${view}?${query}`);
  const applications=useResearch<ResearchPage>(['companies','products','roles'].includes(view)?`/api/v2/applications?release_id=${release}&limit=100`:null);
  const roles=useResearch<ResearchPage>(view==='companies'?`/api/v2/roles?release_id=${release}&limit=100`:null);
  const segments=useResearch<ResearchPage>(view==='companies'?`/api/v2/segments?release_id=${release}&limit=100`:null);
  function change(key:string,value:string){router.push(indexHref(view,{...filters,[key]:value}),{scroll:false})}
  return <section className="rs-directory" aria-label={directoryNames[view]+'清單'}>
    <nav className="rs-directory-tabs" aria-label="研究目錄分類">{(Object.keys(directoryNames) as DirectoryView[]).map(key=><Link key={key} href={indexHref(key)} aria-current={view===key?'page':undefined}>{directoryNames[key]}</Link>)}</nav>
    {view==='companies'&&<p className="rs-directory-note">同一公司的跨環節角色合併為一份研究；產品能力與具名交易分開核對。</p>}
    <div className="rs-directory-filters">
      {view==='companies'&&<><label>上市市場<select value={market} onChange={event=>change('market',event.target.value)}><option value="">全部市場與未上市公司</option>{Object.entries({TW:'台灣',US:'美國',KR:'韓國',JP:'日本',DE:'德國',NL:'荷蘭',HK:'香港'}).map(([key,name])=><option key={key} value={key}>{name}</option>)}</select></label>
        <label>供應角色或環節<select value={role} onChange={event=>change('role',event.target.value)}><option value="">全部角色與環節</option><optgroup label="產品供應角色">{roles.data?.data.items.map(row=><option key={row.id} value={row.id}>{row.name}</option>)}</optgroup><optgroup label="產業環節">{segments.data?.data.items.map(row=><option key={row.id} value={row.id}>{row.name}</option>)}</optgroup></select></label></>}
      {['companies','products','roles'].includes(view)&&<label>應用範圍<select value={category} onChange={event=>change('category',event.target.value)}><option value="">全部應用</option>{applications.data?.data.items.map(row=><option key={row.id} value={row.id}>{row.name}</option>)}</select></label>}
      {(market||role||category)&&<Link href={indexHref(view)}>清除篩選</Link>}
    </div>
    {(applications.error||roles.error||segments.error)&&<p>部分分類選單目前無法讀取，仍可使用完整目錄或搜尋。</p>}
    {(applications.data?.data.has_more||roles.data?.data.has_more||segments.data?.data.has_more)&&<p>更多供應角色可由應用研究繼續展開。</p>}
    {result.error?<div role="alert"><p>{result.error}</p><Link href={indexHref(view)}>重新開啟完整目錄</Link></div>:result.loading?<p role="status">正在讀取目錄…</p>:result.data&&<>
      {!result.data.data.items.length&&<p>{market||role||category?'此範圍尚未列出研究，可清除篩選或從其他分類繼續。':'此分類尚未建立研究，可由環節或其他分類繼續閱讀。'}</p>}
      <ul>{result.data.data.items.map(row=><li key={row.id}><Link href={href(row.id)}><strong>{row.name}</strong><span>{row.summary}</span><span className="rs-list-action">閱讀研究</span></Link></li>)}</ul>
      <div className="rs-directory-pages">{cursor&&<Link href={indexHref(view,filters)}>回第一頁</Link>}{result.data.data.has_more&&<Link className="button" href={indexHref(view,{...filters,cursor:result.data.data.next_cursor||''})}>下一頁</Link>}</div>
    </>}
  </section>;
}
