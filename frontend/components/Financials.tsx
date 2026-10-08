import {basisLabel,dateLabel} from '@/lib/api';
import type {Financial} from '@/lib/types';

export function metric(value:number|null|undefined,kind:string,currency?:string) {
  if(value==null)return '尚未取得';
  if(kind==='revenue')return `${new Intl.NumberFormat('zh-TW',{notation:'compact',maximumFractionDigits:2}).format(value)} ${currency}`;
  return `${new Intl.NumberFormat('zh-TW',{maximumFractionDigits:2}).format(value)}${kind==='eps'?` ${currency}/股`:'%'}`;
}
export function Financials({rows,compact=false}:{rows:Financial[];compact?:boolean}) {
  if(!rows.length)return <p className="empty">尚未取得官方財報。可從下方官方事件開啟來源，或查看來源更新狀態。</p>;
  const latest=rows.find(r=>r.basis!=='monthly')||rows[0];
  return <><div className="financial-heading"><strong>{latest.period}</strong><span>{basisLabel[latest.basis]||latest.basis} · {latest.currency}</span><a href={latest.url} target="_blank" rel="noreferrer">官方來源 ↗</a></div><div className="metrics">{[['revenue','營收'],['revenue_yoy','營收年增率'],['gross_margin','毛利率'],['eps','EPS']].map(([key,label])=><div key={key}><span>{label}</span><strong>{metric(latest[key as keyof Financial] as number|null,key,latest.currency)}</strong></div>)}</div><p className="data-note">發布／出表：{dateLabel(latest.published_at)}；取得：{dateLabel(latest.fetched_at)}。金額採原幣；各公司年度與期間可能不同。</p>{!compact&&<details><summary>查看其他期間與月營收</summary><div className="table-scroll"><table><thead><tr><th>期間／口徑</th><th>營收</th><th>年增率</th><th>毛利率</th><th>EPS</th><th>來源</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><th>{r.period}<small>{basisLabel[r.basis]} / {r.currency}</small></th><td>{metric(r.revenue,'revenue',r.currency)}</td><td>{metric(r.revenue_yoy,'revenue_yoy')}</td><td>{metric(r.gross_margin,'gross_margin')}</td><td>{metric(r.eps,'eps',r.currency)}</td><td><a href={r.url} target="_blank" rel="noreferrer">原始資料 ↗</a></td></tr>)}</tbody></table></div></details>}</>
}
