import {test,expect,Page} from '@playwright/test';

const key='industryflow.research-watchlist.v2';
const shown='11111111-1111-4111-8111-111111111111',newer='22222222-2222-4222-8222-222222222222';
type Seen={research:string|null;values:string|null;events:number|null};
type Target={kind:string;id:string;seen?:Seen};
const summary=(id:string,name:string)=>({id,kind:id.split('-')[0],name,summary:'合成收藏測試資料',reviewed:'2026-10-17'});

// A synthetic server: per-object tokens and an append-only event list, like the real contract.
async function server(page:Page){
  const state={release:shown,research:{'company-sample':'r1','product-sample':'p1'} as Record<string,string>,values:'v1',
    events:[] as {id:number;entity:string;dated:boolean}[],fail:false,queries:[] as {release_id?:string;items:Target[]}[]};
  await page.route('**/api/v2/**',async route=>{
    const request=route.request(),url=new URL(request.url()),path=url.pathname.replace('/api/v2/','');
    if(request.method()==='POST'&&path==='updates/query'){
      const body=request.postDataJSON() as {release_id?:string;items:Target[]};state.queries.push(body);
      if(state.fail)return route.fulfill({status:503,json:{code:'database-unavailable',message:'目前無法讀取研究，請稍後再試。',retryable:true}});
      const items=body.items.map(item=>{
        if(!(item.id in state.research))return {kind:item.kind,id:item.id,available:false,reason:'這份研究不在目前已發布版本中，可能已改名、合併或封存。'};
        const events=state.events.filter(event=>event.entity===item.id),marker=Math.max(0,...events.map(event=>event.id));
        const after=events.filter(event=>item.seen?.events!=null&&event.id>item.seen.events);
        const values=item.kind==='company'?state.values:null;
        return {kind:item.kind,id:item.id,available:true,name:item.id==='company-sample'?'合成公司':'合成冷板',
          research:{token:state.research[item.id],changed:item.seen?.research==null?null:item.seen.research!==state.research[item.id]},
          values:{applicable:values!==null,token:values,changed:values===null?false:item.seen?.values==null?null:item.seen.values!==values},
          events:{marker,changed:item.seen?.events==null?null:after.length>0,new_dated:after.filter(e=>e.dated).length,new_undated:after.filter(e=>!e.dated).length}};
      });
      return route.fulfill({headers:{'Cache-Control':'no-store'},json:{release_id:state.release,schema_version:'research-v1',data:{as_of:'2026-10-18T00:00:00Z',release_id:state.release,items,note:'合成'}}});
    }
    let data:unknown;
    if(path==='manifest')data={published_at:'2026-10-18',generation:1};
    else if(path==='graphs')data={root:url.searchParams.get('root'),nodes:[],edges:[],truncated:false,continue_from:[]};
    else if(path.includes('/financials'))data={as_of:'2026-10-18T00:00:00Z',items:[],has_more:false,next_cursor:null,gaps:[],source_selection_gap:null};
    else if(path.startsWith('companies/'))data={...summary('company-sample','合成公司'),markdown:'## 供應角色\n\n合成角色。\n\n## 研究界線\n\n合成界線。',content:{},claims:[],related:[],assets:[],truncated:false};
    else if(path.startsWith('products/'))data={...summary('product-sample','合成冷板'),markdown:'## 定義與用途\n\n合成產品。',content:{},claims:[],related:[],assets:[],truncated:false};
    else data={...summary('concept-sample','合成術語'),markdown:'## 中文解釋\n\n合成術語。',content:{},claims:[],related:[],assets:[],truncated:false};
    return route.fulfill({json:{release_id:state.release,schema_version:'research-v1',data}});
  });
  return state;
}
const stored=(page:Page)=>page.evaluate(k=>JSON.parse(localStorage.getItem(k)||'null'),key);
const card=(page:Page,name:string)=>page.locator('.rs-watch-card').filter({has:page.getByRole('heading',{name})});

test('收藏以畫面版本建立基準，研究／數值／事件分開，已讀只記錄顯示內容',async({page})=>{
  const state=await server(page);
  await page.goto('/next?focus=company-sample&release_id='+shown);
  await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('已加入收藏',{exact:true})).toBeVisible();
  expect(state.queries.at(-1)).toEqual({release_id:shown,items:[{kind:'company',id:'company-sample'}]});
  expect((await stored(page)).targets[0].seen).toEqual({research:'r1',values:'v1',events:0});
  // A site-wide release where this company did not change is not an update; values and events are.
  state.release=newer;state.values='v2';state.events.push({id:11,entity:'company-sample',dated:true},{id:12,entity:'company-sample',dated:false});
  await page.getByRole('navigation',{name:'研究導覽'}).getByRole('link',{name:'此裝置收藏'}).click();
  const company=card(page,'合成公司');
  await expect(company).toContainText('研究無變更');await expect(company).toContainText('有效數值有新期或修訂');
  await expect(company).toContainText('1 則新事件（依發布日）；1 則新收錄，發布日未知，不代表剛發生');
  await expect(page.getByText('不含研究全文',{exact:false})).toBeVisible();
  // The server moves on after this response; marking read must not swallow event 13.
  state.events.push({id:13,entity:'company-sample',dated:true});
  await company.getByRole('button',{name:'將目前顯示標為已讀'}).click();
  await expect(company).toContainText('沒有新事件');await expect(company).toContainText('數值無變更');
  expect((await stored(page)).targets[0].seen).toEqual({research:'r1',values:'v2',events:12});
  await page.getByRole('button',{name:'檢查收藏更新'}).click();await expect(company).toContainText('1 則新事件（依發布日）');
  await page.reload();await expect(company).toContainText('1 則新事件（依發布日）');
});

test('無法建立基準時標待確認，不會自動全部已讀',async({page})=>{
  const state=await server(page);state.fail=true;
  await page.goto('/next?focus=product-sample&release_id='+shown);
  await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText(/已讀基準/)).toBeVisible();
  expect((await stored(page)).targets[0].seen).toEqual({research:null,values:null,events:null});
  state.fail=false;state.events.push({id:3,entity:'product-sample',dated:true});
  await page.goto('/next?view=watchlist&release_id='+shown);
  const product=card(page,'合成冷板');
  await expect(product.getByText('待確認：尚未建立已讀基準')).toHaveCount(2);await expect(product).not.toContainText('數值');
  await product.getByRole('button',{name:'以目前顯示建立已讀基準'}).click();
  await expect(product).toContainText('研究無變更');await expect(product).toContainText('沒有新事件');
});

test('只有四類可收藏、上限 100、失效項目可移除',async({page})=>{
  await server(page);
  await page.goto('/next?focus=concept-sample&release_id='+shown);await expect(page.getByRole('heading',{name:'合成術語',level:1})).toBeVisible();
  await expect(page.getByRole('button',{name:'加入收藏'})).toHaveCount(0);
  const full=Array.from({length:100},(_,index)=>({kind:'company',id:`company-full-${index}`,name:`合成 ${index}`,seen:{research:null,values:null,events:null}}));
  await page.evaluate(([k,targets])=>localStorage.setItem(k as string,JSON.stringify({schema_version:2,targets})),[key,full] as const);
  await page.goto('/next?focus=product-sample&release_id='+shown);await page.getByRole('button',{name:'加入收藏'}).click();
  await expect(page.getByText('最多收藏 100 項',{exact:false})).toBeVisible();expect((await stored(page)).targets).toHaveLength(100);
  await page.evaluate(k=>localStorage.setItem(k,JSON.stringify({schema_version:2,targets:[{kind:'company',id:'company-retired',name:'已封存公司',seen:{research:'x',values:'y',events:1}}]})),key);
  await page.goto('/next?view=watchlist&release_id='+shown);
  const retired=card(page,'已封存公司');await expect(retired).toContainText('可能已改名、合併或封存');
  await retired.getByRole('button',{name:'移除收藏'}).click();await expect(page.getByText('尚未收藏研究',{exact:false})).toBeVisible();
});

test('部分損壞保留有效項目',async({page})=>{
  await server(page);
  await page.addInitScript(k=>localStorage.setItem(k,JSON.stringify({schema_version:2,targets:[
    {kind:'company',id:'company-sample',name:'合成公司',seen:{research:'r1',values:'v1',events:0}},{kind:'segment',id:'segment-x',name:'非收藏類型',seen:{}},'broken']})),key);
  await page.goto('/next?view=watchlist&release_id='+shown);
  await expect(page.getByText('部分收藏內容損壞',{exact:false})).toBeVisible();
  await expect(card(page,'合成公司')).toContainText('研究無變更');await expect(page.locator('.rs-watch-card')).toHaveCount(1);
});

test('儲存被拒絕仍可在手機收藏並閱讀更新',async({page})=>{
  await server(page);
  await page.addInitScript(()=>Object.defineProperty(Storage.prototype,'setItem',{value(){throw new Error('blocked')}}));
  await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=company-sample&release_id='+shown);
  await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('記憶體暫存',{exact:false})).toBeVisible();
  await page.getByRole('navigation',{name:'研究導覽'}).getByRole('link',{name:'此裝置收藏'}).click();
  await expect(card(page,'合成公司')).toContainText('研究無變更');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
