// Only the existing map's bounded selection is allowed as a return location.
export function mapReturn(value:string|null):string|undefined{
  if(!value||!value.startsWith('/?')||value.length>600)return;
  const url=new URL(value,'https://industryflow.invalid');
  if(url.origin!=='https://industryflow.invalid'||url.pathname!=='/')return;
  const layer=url.searchParams.get('layer'),segment=url.searchParams.get('segment'),relation=url.searchParams.get('relation');
  if(!layer||!['ai-server','semiconductor'].includes(layer)||!segment||!/^[-a-z0-9]{1,100}$/.test(segment))return;
  const query=new URLSearchParams({layer,segment});
  if(relation&&/^[-a-z0-9]{1,200}$/.test(relation))query.set('relation',relation);
  return '/?'+query;
}

// Rebuild a directory URL instead of accepting an arbitrary redirect destination.
export function directoryReturn(value:string|null,release?:string,from?:string):string|undefined{
  if(!value||!value.startsWith('/next?')||value.length>2400)return;
  const params=new URL(value,'https://industryflow.invalid').searchParams;
  const view=params.get('view');
  if(!view||!['segments','applications','roles','products','companies','themes','concepts'].includes(view))return;
  const result=new URLSearchParams({view,...(release?{release_id:release}:{}),...(from?{from}:{})});
  for(const key of ['market','role','category','cursor']){const item=params.get(key);if(item&&item.length<=1024)result.set(key,item)}
  return '/next?'+result;
}
