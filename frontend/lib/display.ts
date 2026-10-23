import type {Confidence} from './types';

export const confidenceLabel:Record<Confidence,string>={
  'well-supported':'有明確證據支持',inference:'有條件推論','needs-verification':'仍待核實',
};
export const sourceStatus:Record<string,string>={manual:'人工研究入口',not_run:'尚未執行',success:'取得成功',partial:'部分取得',failed:'取得失敗',configuration_required:'待設定',unregistered:'尚未註冊',unverified:'可讀性待確認',available:'已有數值',stale:'資料過舊',unavailable:'尚未取得'};
export const lifecycleLabel:Record<string,string>={emerging:'萌芽',validating:'驗證中',scaling:'擴張',mature:'成熟',fading:'降溫'};
export const fieldLabel:Record<string,string>={assessment:'判讀',summary:'結論',confidence:'支持程度',reviewed:'查核日',status:'狀態',checked:'查核基準',claims:'論點',evidence:'證據',conditions:'條件',gaps:'缺口',milestone_reviews:'里程碑核對',next_checks:'下一確認點',paths:'傳導假設',statement:'論述',stance:'證據方向',supporting:'支持',counter:'反向',excerpt:'必要摘錄',period:'資料期間',published:'發布日',url:'原始來源',source_id:'來源',id:'識別',steps:'路徑',from:'起點',to:'終點',type:'關係',mechanism:'傳導機制',direction:'方向',evidence_ids:'引用證據',claim_ids:'引用論點',question:'問題',evidence_required:'所需證據',milestone_id:'里程碑',state:'核對結果',note:'核對說明',occurred:'發生日期',change_reason:'修改原因',name_zh:'名稱',segments:'相關環節',beneficiaries:'候選公司',milestones:'預期里程碑',event:'事件',date:'日期',positive:'可能正向',negative:'可能負向',mixed:'影響混合',unknown:'尚未確認',confirmed:'已確認',contradicted:'已被反證',unconfirmed:'尚未確認',upstream:'上游',downstream:'下游',sibling:'共同下游手足',theme:'題材擴散'};
export const unitLabel:Record<string,string>={currency:'金額',percent:'%', 'percentage-point':'百分點',count:'個',units:'件',watt:'W',kilowatt:'kW'};
export const displayName=(id:string,names:Record<string,string>)=>names[id]||'名稱待補';
export const statusLabel=(value:string)=>sourceStatus[value]||lifecycleLabel[value]||'狀態待確認';
export const readingGap=(value:string)=>/HTTP|Error|timeout|來源 [a-z0-9]/i.test(value)?'來源目前取得受限，既有研究與觀測保留。':readingText(value);

/** Presentation only: integer arithmetic rounds decimal strings without changing API precision. */
export function readableNumber(value:string|number|null|undefined,unit='',currency:string|null=null){
  if(value===null||value===undefined)return '尚未取得';
  const raw=String(value),match=/^(-?)(\d+)(?:\.(\d+))?$/.exec(raw);
  const suffix=unit==='currency'||unit==='amount'?(currency||'幣別未提供'):unit==='per-share'?`${currency||'幣別未提供'}/股`:(unitLabel[unit]||unit);
  if(!match)return `數值待確認${suffix?' '+suffix:''}`;
  const digits=match[2].replace(/^0+(?=\d)/,''),fraction=match[3]||'';
  const scale=(unit==='percent'||unit==='percentage-point')?0:digits.length>8?8:digits.length>4?4:0;
  const divisor=10n**BigInt(fraction.length+scale);
  const amount=BigInt(digits+fraction);
  const rounded=(amount*100n+divisor/2n)/divisor;
  const integer=(rounded/100n).toString().replace(/\B(?=(\d{3})+(?!\d))/g,',');
  const decimals=(rounded%100n).toString().padStart(2,'0').replace(/0+$/,'');
  return `${match[1]&&amount!==0n?'-':''}${integer}${decimals?'.'+decimals:''}${scale===8?' 億':scale===4?' 萬':''}${suffix?' '+suffix:''}`;
}

export function readingText(value:string,names:Record<string,string>={}){
  const authoring:Record<string,string>={beneficiaries:'候選公司清單','companies.role':'公司供應角色',role:'供應角色',kpis:'監測指標',upstream:'上游供應',downstream:'下游需求',tier:'供應角色層級',none:'未列代表公司','tw: none':'未列台股代表公司','tw: present':'已列台股代表公司','market_coverage.us: none':'未列美股主要供應者','led_by: [TW]':'台灣主導','led_by: [US]':'美國主導','led_by: [JP]':'日本主導'};
  if(authoring[value])return authoring[value];
  return value.replace(/\bthemes\/([a-z0-9-]+)\.md\b/g,(_match,id)=>`${names[id]||'相關'}題材`)
    .replace(/\b([a-z][a-z0-9-]*)\.(upstream|downstream|themes)\b/g,(_match,id,field)=>`${names[id]||'該環節'}的${({upstream:'上游供應',downstream:'下游需求',themes:'相關題材'} as Record<string,string>)[field]}`)
    .replace(/\b(?:well-supported|needs[ -]verification|inference)\b/g,word=>confidenceLabel[word.replace(' ','-') as Confidence]||word)
    .replace(/\b(?:emerging|validating|scaling|mature|fading)\b/g,word=>lifecycleLabel[word])
    .replace(/\b[a-z][a-z0-9]*(?:-[a-z0-9]+)*\b/g,word=>names[word]||word);
}

export function readTime(value:string){return new Intl.DateTimeFormat('zh-TW',{dateStyle:'short',timeStyle:'short',timeZone:'Asia/Taipei'}).format(new Date(value))}
