import {basisLabel,dateLabel} from '@/lib/api';
import type {Financial} from '@/lib/types';
import {readableNumber} from '@/lib/display';
import {NumberValue} from './Reading';

export function metric(value:number|null|undefined,kind:string,currency?:string) {
  return readableNumber(value,kind==='revenue'?'amount':kind==='eps'?'per-share':'percent',currency);
}
export function Financials({rows,compact=false}:{rows:Financial[];compact?:boolean}) {
  if(!rows.length)return <p className="empty">尚未取得官方財報。可從下方官方事件開啟來源，或查看來源更新狀態。</p>;
  const latest=rows.find(r=>r.basis!=='monthly')||rows[0];
  return <><div className="financial-heading"><strong>{latest.period}</strong><span>{basisLabel[latest.basis]||latest.basis} · {latest.currency}</span><a href={latest.url} target="_blank" rel="noreferrer">官方來源 ↗</a></div><div className="metrics">{[['revenue','營收'],['revenue_yoy','營收年增率'],['gross_margin','毛利率'],['eps','EPS']].map(([key,label])=><div key={key}><span>{label}</span><div className="financial-value"><NumberValue value={latest[key as keyof Financial] as number|null} unit={key==='revenue'?'amount':key==='eps'?'per-share':'percent'} currency={latest.currency}/></div></div>)}</div><p className="data-note">發布／出表：{dateLabel(latest.published_at)}；取得：{dateLabel(latest.fetched_at)}。金額採原幣；各公司年度與期間可能不同。</p>{!compact&&<details><summary>查看其他期間與月營收</summary><div className="table-scroll"><table><thead><tr><th>期間／口徑</th><th>營收</th><th>年增率</th><th>毛利率</th><th>EPS</th><th>來源</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><th>{r.period}<small>{basisLabel[r.basis]} / {r.currency}</small></th><td><NumberValue value={r.revenue} unit="amount" currency={r.currency}/></td><td><NumberValue value={r.revenue_yoy} unit="percent"/></td><td><NumberValue value={r.gross_margin} unit="percent"/></td><td><NumberValue value={r.eps} unit="per-share" currency={r.currency}/></td><td><a href={r.url} target="_blank" rel="noreferrer">原始資料 ↗</a></td></tr>)}</tbody></table></div></details>}</>
}
