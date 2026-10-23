import {Page} from '@playwright/test';

export const key='industryflow.research-watchlist.v2';
export const legacyKey='industryflow.theme-watchlist.v1';
export const shown='11111111-1111-4111-8111-111111111111',newer='22222222-2222-4222-8222-222222222222';
type Seen={research:string|null;values:string|null;events:number|null};
type Target={kind:string;id:string;seen?:Seen};
const summary=(id:string,name:string)=>({id,kind:id.split('-')[0],name,summary:'合成收藏測試資料',reviewed:'2026-10-17'});
const names:Record<string,string>={'company-sample':'合成公司','product-sample':'合成冷板','theme-liquid-cooling':'合成液冷題材'};

// A synthetic server: per-object tokens and an append-only event list, like the real contract.
export async function server(page:Page){
  const state={release:shown,research:{'company-sample':'r1','product-sample':'p1','theme-liquid-cooling':'t1'} as Record<string,string>,
    themeValues:'i1',events:[] as {id:number;entity:string;dated:boolean}[],fail:false,queries:[] as {release_id?:string;items:Target[]}[]};
  await page.route('**/api/v2/**',async route=>{
    const request=route.request(),url=new URL(request.url()),path=url.pathname.replace('/api/v2/','');
    if(request.method()==='POST'&&path==='updates/query'){
      const body=request.postDataJSON() as {release_id?:string;items:Target[]};state.queries.push(body);
      if(state.fail)return route.fulfill({status:503,json:{code:'database-unavailable',message:'目前無法讀取研究，請稍後再試。',retryable:true}});
      const items=body.items.map(item=>{
        if(!(item.id in state.research))return {kind:item.kind,id:item.id,available:false,reason:'這份研究不在目前已發布版本中，可能已改名、合併或封存。'};
        const events=state.events.filter(event=>event.entity===item.id),marker=Math.max(0,...events.map(event=>event.id));
        const after=events.filter(event=>item.seen?.events!=null&&event.id>item.seen.events);
        // Company financial statements were removed; only themes still carry tracked values.
        const values=item.kind==='theme'?state.themeValues:null;
        return {kind:item.kind,id:item.id,available:true,name:names[item.id],
          research:{token:state.research[item.id],changed:item.seen?.research==null?null:item.seen.research!==state.research[item.id]},
          values:{applicable:values!==null,token:values,changed:values===null?false:item.seen?.values==null?null:item.seen.values!==values},
          events:{marker,changed:item.seen?.events==null?null:after.length>0,new_dated:after.filter(e=>e.dated).length,new_undated:after.filter(e=>!e.dated).length}};
      });
      return route.fulfill({headers:{'Cache-Control':'no-store'},json:{release_id:state.release,schema_version:'research-v1',data:{as_of:'2026-10-18T00:00:00Z',release_id:state.release,items,note:'合成'}}});
    }
    let data:unknown;
    if(path==='manifest')data={published_at:'2026-10-18',generation:1};
    else if(path==='graphs')data={root:url.searchParams.get('root'),nodes:[],edges:[],truncated:false,continue_from:[]};
    else if(path==='events'||path==='observations')data={as_of:'2026-10-18T00:00:00Z',items:[],has_more:false,next_cursor:null};
    else if(path.startsWith('companies/'))data={...summary('company-sample','合成公司'),markdown:'## 供應角色\n\n合成角色。\n\n## 研究界線\n\n合成界線。',content:{},claims:[],related:[],assets:[],truncated:false};
    else if(path.startsWith('products/'))data={...summary('product-sample','合成冷板'),markdown:'## 定義與用途\n\n合成產品。',content:{},claims:[],related:[],assets:[],truncated:false};
    else data={...summary('concept-sample','合成術語'),markdown:'## 中文解釋\n\n合成術語。',content:{},claims:[],related:[],assets:[],truncated:false};
    return route.fulfill({json:{release_id:state.release,schema_version:'research-v1',data}});
  });
  return state;
}
export const stored=(page:Page,name=key)=>page.evaluate(k=>JSON.parse(localStorage.getItem(k)||'null'),name);
export const card=(page:Page,name:string)=>page.locator('.rs-watch-card').filter({has:page.getByRole('heading',{name})});
export const pending={research:null,values:null,events:null};
