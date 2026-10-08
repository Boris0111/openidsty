export function Status({loading,error,retry}:{loading?:boolean;error?:string;retry?:()=>void}) {
  if(loading)return <div className="status-box" role="status"><span className="loading-dot"/>正在取得資料…</div>;
  if(error)return <div className="status-box error" role="alert"><p>{error}</p>{retry&&<button onClick={retry}>重新取得</button>}</div>;
  return null;
}
