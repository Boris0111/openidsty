'use client';

export function ResearchReadStatus({state}:{state:{refreshError?:string;refresh:()=>void}}){
  return state.refreshError?<p className="rs-scope-note" role="status">目前無法更新，先保留上次成功讀取的內容。<button onClick={state.refresh}>重試更新</button></p>:null;
}
