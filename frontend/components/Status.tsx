export function Status({loading,error,retry}:{loading?:boolean;error?:string;retry?:()=>void}) {
  if(loading)return <div className="status-box" role="status"><span className="loading-dot"/>正在取得資料…</div>;
  if(error)return <div className="status-box error" role="alert"><p>{/not found|找不到|不存在/i.test(error)?'找不到這項資料，請返回清單重新選擇。':'此區資料暫時無法取得，請稍後重新取得。已載入的研究仍可閱讀。'}</p>{retry&&<button onClick={retry}>重新取得</button>}</div>;
  return null;
}
