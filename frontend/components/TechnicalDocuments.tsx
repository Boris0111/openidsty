'use client';
import {useApi} from '@/lib/api';
import {Status} from './Status';

export const documentKind:Record<string,string>={'formal-specification':'正式規範',draft:'草案',roadmap:'路線圖','vendor-explanation':'廠商說明',informative:'技術說明'};
type Version={id:string;label:string|null;url:string;published:string|null;reviewed:string;'read-scope':string;'access-limitations':string;scope:string;locators:{id:string;section:string;excerpt:string}[]};
type DocumentDetail={definition:{title:string;publisher:string;'doc-kind':string;versions:Version[]}};

export function DocumentCitation({id,version,locator}:{id:string;version?:string;locator?:string}){
  const api=useApi<DocumentDetail>(`/api/technical-documents/${encodeURIComponent(id)}?limit=10&offset=0`);
  // A missing fixed reference must never silently use a newer document.
  const selected=api.data?.definition.versions.find(v=>v.id===version);
  const excerpt=selected?.locators.find(l=>l.id===locator);
  return <div className="document-citation"><Status {...api}/>{api.data&&(selected&&excerpt?<>
    <a href={selected.url} target="_blank" rel="noreferrer">{api.data.definition.title} ↗</a>
    <p className="data-note">{documentKind[api.data.definition['doc-kind']]||'文件性質待確認'}{selected.label&&`・${selected.label}`}；{excerpt.section}</p>
    <blockquote>{excerpt.excerpt}</blockquote><p className="data-note">引用範圍：{selected['read-scope']}</p>
  </>:<p>這項引用的版本或章節暫時無法確認，請保留此證據缺口。</p>)}</div>;
}

// Keep shared citation URLs readable, without showing monitoring work queues.
export function TechnicalDocumentReading({id,version}:{id:string;version:string|null}){
  const api=useApi<DocumentDetail>(`/api/technical-documents/${encodeURIComponent(id)}?limit=10&offset=0`),d=api.data;
  const chosen=(d?.definition.versions||[]).filter(v=>!version||v.id===version);
  return <div className="page-content document-reading"><Status {...api}/>{d&&<>
    <h1>{d.definition.title}</h1><p className="data-note">{d.definition.publisher}・{documentKind[d.definition['doc-kind']]||'文件性質待確認'}</p>
    {version&&!chosen.length&&<p role="status">找不到引用的版本，請返回研究內容核實。</p>}
    {chosen.map(v=><section key={v.id}><h2>{v.label||'版本未標示'}</h2><p>發布 {v.published||'日期未標示'}；查核 {v.reviewed}</p>
      <p>適用範圍：{v.scope}</p><p>引用範圍：{v['read-scope']}</p><p>{v['access-limitations']}</p>
      <a href={v.url} target="_blank" rel="noreferrer">閱讀官方原始文件 ↗</a>
      {v.locators.map(l=><article key={l.id} id={`locator-${l.id}`}><h3>{l.section}</h3><blockquote>{l.excerpt}</blockquote></article>)}
    </section>)}
  </>}</div>;
}
