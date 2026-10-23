import {test,expect} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';
import {server,stored,card,key,shown,newer} from './watchlist-fixture';

test('收藏以畫面版本建立基準，研究／數值／事件分開，已讀只記錄顯示內容',async({page})=>{
  const state=await server(page);
  await page.goto('/next?focus=company-sample&release_id='+shown);
  await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('已加入收藏',{exact:true})).toBeVisible();
  expect(state.queries.at(-1)).toEqual({release_id:shown,items:[{kind:'company',id:'company-sample'}]});
  expect((await stored(page)).targets[0].seen).toEqual({research:'r1',values:'v1',events:0});
  // A site-wide release where this company did not change is not an update; values and events are.
  state.release=newer;state.values='v2';state.events.push({id:11,entity:'company-sample',dated:true},{id:12,entity:'company-sample',dated:false});
  await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'收藏',exact:true}).click();
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
  await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'收藏',exact:true}).click();
  await expect(card(page,'合成公司')).toContainText('研究無變更');
  await expectNoHorizontalOverflow(page,0);
});
