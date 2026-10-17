'use client';
import {useState} from 'react';
import {useResearch,ResearchCitation as Citation,ResearchDocument} from '@/lib/research-api';

export function ResearchCitation({source,release}:{source:Citation;release?:string}){
  const [open,setOpen]=useState(false);
  const path=release&&open?`/api/v2/documents/${encodeURIComponent(source.document_id)}/revisions/${encodeURIComponent(source.revision_id)}?release_id=${encodeURIComponent(release)}`:null;
  const result=useResearch<ResearchDocument>(path);
  // Owner preview uses the embedded candidate citation and never calls public draft URLs.
  const document=release?result.data?.data:source;
  const matching=document?.locators?.filter(locator=>locator.id===source.locator||locator.section===source.locator)||[];
  const readScope=document?.read_scope?.split(/[，；]/).filter(part=>!/(HTTP\s*[1-5]\d\d|JavaScript.*外殼|parser.*(診斷|錯誤))/i.test(part)).map(part=>part.replace(/^以瀏覽器讀取/,'已讀')).join('；');
  return <div className="rs-citation">
    {source.stance==='counter'&&<strong>反向證據</strong>}
    <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
    <span>{source.applicable_period}</span><span>引用位置：{source.locator}</span>
    <details onToggle={event=>setOpen(event.currentTarget.open)}><summary>查閱這份引用</summary>
      {result.loading?<p role="status">正在讀取引用…</p>:result.error?<p role="status">這份研究引用的文件版本目前無法讀取。原判斷與引用位置保留，可由上方連結查閱原始來源。</p>:document&&<div className="rs-citation-reading">
        {document.document_kind&&['normative','draft','roadmap'].includes(document.document_kind)&&<p>文件性質：{({normative:'正式規範',draft:'草案',roadmap:'路線圖'} as Record<string,string>)[document.document_kind]}</p>}
        {document.published&&<p>文件日期：{document.published}</p>}
        {document.scope&&<p>{document.scope}</p>}
        {readScope&&<p>本研究讀取範圍：{readScope}</p>}
        {matching.map((locator,index)=><div key={index}>{locator.page!=null&&<p>頁碼：{locator.page}</p>}{locator.excerpt&&<blockquote>{locator.excerpt}</blockquote>}</div>)}
        {document.access_limitations&&<p>{document.access_limitations}</p>}
        {!matching.some(locator=>locator.excerpt)&&<p>此引用保留原文定位，未保存該段全文。</p>}
      </div>}
    </details>
  </div>;
}
