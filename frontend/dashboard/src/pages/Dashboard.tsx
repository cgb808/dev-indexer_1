import React, { useEffect, useState, useRef, useCallback } from 'react';

interface RuntimeStat { metric:string; window:string; count:number; avg:number; p50:number; p95:number; }
interface QueueCount { status:string; count:number; }
interface MetricsResponse { ts:string; windows?:string[]; queue?:QueueCount[]; queue_oldest_pending_age_s?:number; doc_embeddings?:{count:number}[]; runtime_stats?:Record<string, RuntimeStat[]>; ingest_log?:Record<string, {status:string; count:number}[]>; error?:string; }

const DISABLE_METRICS = ((import.meta as any).env?.VITE_DISABLE_METRICS === '1');
const METRICS_ENDPOINT = (import.meta as any).env?.VITE_METRICS_URL || '/metrics/dashboard';
// New: fine grained polling controls
const DISABLE_POLLING = ((import.meta as any).env?.VITE_DISABLE_METRICS_POLLING === '1');
const POLL_INTERVAL_MS = parseInt((import.meta as any).env?.VITE_METRICS_POLL_INTERVAL_MS || '30000', 10);
const MIN_MANUAL_REFRESH_INTERVAL_MS = parseInt((import.meta as any).env?.VITE_METRICS_MANUAL_COOLDOWN_MS || '5000', 10);

const Spark: React.FC<{ points:number[]; color?:string }> = ({ points, color='#58a6ff' }) => {
  const ref = useRef<HTMLCanvasElement|null>(null);
  useEffect(()=>{ const el=ref.current; if(!el) return; const w=(el.width=el.clientWidth); const h=(el.height=el.clientHeight); const ctx=el.getContext('2d'); if(!ctx) return; ctx.clearRect(0,0,w,h); if(!points.length) return; const min=Math.min(...points); const max=Math.max(...points); const span=max-min || 1; ctx.strokeStyle=color; ctx.lineWidth=1.25; ctx.beginPath(); points.forEach((v,i)=>{ const x=(i/(points.length-1))*(w-2)+1; const y=h-((v-min)/span)*(h-2)-1; i?ctx.lineTo(x,y):ctx.moveTo(x,y);}); ctx.stroke(); },[points,color]);
  return <canvas ref={ref} className='spark' style={{width:'100%'}} />;
};

export const Dashboard: React.FC = () => {
  const [data,setData] = useState<MetricsResponse|null>(null);
  const [err,setErr] = useState<string|null>(null);
  const [loading,setLoading] = useState(false);
  const [history,setHistory] = useState<Record<string, number[]>>({});
  const [apiKey,setApiKey] = useState('');
  const [selectedWindow,setSelectedWindow] = useState('5m');
  const [showChat,setShowChat] = useState(false);
  const [metricsEnabled,setMetricsEnabled] = useState(false); // new explicit gate
  const [lastFetch,setLastFetch] = useState<number>(0); // for manual rate limit
  const [cooldown,setCooldown] = useState<number>(0);
  const MAX_HISTORY=80;

  const fetchMetrics = useCallback(async ()=>{
    const now = Date.now();
    if(now - lastFetch < MIN_MANUAL_REFRESH_INTERVAL_MS){
      // ignore rapid manual clicks
      return;
    }
    setLastFetch(now);
    setCooldown(MIN_MANUAL_REFRESH_INTERVAL_MS);
    const cdStart = now;
    // cooldown countdown
    const interval = setInterval(()=>{
      const remain = MIN_MANUAL_REFRESH_INTERVAL_MS - (Date.now() - cdStart);
      if(remain <= 0){ setCooldown(0); clearInterval(interval); } else { setCooldown(remain); }
    },250);

    setLoading(true); setErr(null);
    try { const res = await fetch(METRICS_ENDPOINT,{ headers: apiKey? {'X-Zendexer-Key': apiKey}: {} }); const js = await res.json(); if(!res.ok) throw new Error(js.error||'fetch_failed'); setData(js); if(js?.runtime_stats){ setHistory(h=>{ const next={...h}; Object.values(js.runtime_stats).forEach((arr:any)=>{ arr.forEach((m:any)=>{ const key=m.metric+':'+m.window; const arr2=(next[key] ||= []); arr2.push(m.p50); if(arr2.length>MAX_HISTORY) arr2.splice(0, arr2.length-MAX_HISTORY); });}); return next;}); } } catch(e:any){ setErr(e.message); } finally { setLoading(false); }
  },[apiKey,lastFetch]);

  // Adjusted polling effect: obey DISABLE_POLLING and dynamic interval
  useEffect(()=>{ if(DISABLE_METRICS || DISABLE_POLLING || !metricsEnabled) return; fetchMetrics(); const id=setInterval(fetchMetrics, Math.max(POLL_INTERVAL_MS, 10000)); return ()=>clearInterval(id);},[fetchMetrics, metricsEnabled]);

  return <div className='wrap'>
    <div style={{display:'flex', alignItems:'center', gap:'1rem', flexWrap:'wrap', marginBottom:'.5rem'}}>
      <h1 style={{margin:'0', fontSize:'1.05rem'}}>ZenGlow Metrics</h1>
      <nav style={{display:'flex', gap:'.6rem', fontSize:'.75rem'}}>
        <a href='/dashboard' style={{color:'#8fb4ff', textDecoration:'none'}}>Dashboard</a>
        <a href='/' style={{color:'#8fb4ff', textDecoration:'none'}}>Chat</a>
        <a href='/chat' style={{color:'#8fb4ff', textDecoration:'none'}}>Chat Interface</a>
        <button style={{background: showChat?'#30363d':'#1d2632', border:'1px solid #30363d', padding:'.35rem .7rem', borderRadius:'6px', cursor:'pointer'}} onClick={()=>setShowChat(s=>!s)}>{showChat?'Hide Chat':'Show Embedded Chat'}</button>
        {!DISABLE_METRICS && <button style={{background: metricsEnabled?'#30363d':'#1d2632', border:'1px solid #30363d', padding:'.35rem .7rem', borderRadius:'6px', cursor:'pointer'}} onClick={()=>setMetricsEnabled(m=>!m)}>{metricsEnabled?'Stop Metrics':'Enable Metrics'}</button>}
      </nav>
      <div style={{marginLeft:'auto', display:'flex', gap:'.5rem', alignItems:'center'}}>
        <span style={{fontSize:'.55rem', opacity:.5}}>v0.1</span>
      </div>
    </div>
    <div className='toolbar'>
      <button onClick={fetchMetrics} disabled={loading || !metricsEnabled || cooldown>0}>{loading? 'Refreshing...' : cooldown>0? `Wait ${(cooldown/1000).toFixed(1)}s` : 'Refresh'}</button>
      <input type='password' placeholder='X-Zendexer-Key' value={apiKey} onChange={e=>setApiKey(e.target.value)} />
      {data?.windows && <select value={selectedWindow} onChange={e=>setSelectedWindow(e.target.value)}> {data.windows.map(w=> <option key={w}>{w}</option>)} </select>}
      <span className='small'>Last: {data?.ts || '—'}</span>
    </div>
  {showChat && <div style={{border:'1px solid #30363d', borderRadius:'10px', overflow:'hidden', marginBottom:'1rem'}}>
      <iframe title='chat' src='/chat' style={{width:'100%', height:'540px', border:'0', background:'#0d1117'}} />
    </div>}
  {DISABLE_METRICS && <div style={{color:'#8fb4ff', fontSize:'.75rem', marginTop:'.5rem'}}>Metrics disabled (VITE_DISABLE_METRICS=1). Chat iframe still available.</div>}
  {err && !DISABLE_METRICS && <div style={{color:'#f78166', fontSize:'.8rem'}}>Error: {err}</div>}
  {!DISABLE_METRICS && metricsEnabled && data && <div className='grid'>
      <div className='card'>
        <h3 style={{margin:'0 0 .4rem'}}>Queue</h3>
        <div className='small'>Oldest Pending Age: {data.queue_oldest_pending_age_s ?? '—'} s</div>
        <ul style={{margin:0,paddingLeft:'1.1rem', fontSize:'.7rem'}}>{data.queue?.map(q=> <li key={q.status}>{q.status}: {q.count}</li>)}</ul>
      </div>
      <div className='card'>
        <h3 style={{margin:'0 0 .4rem'}}>Embeddings</h3>
        <div style={{fontSize:'2rem', fontWeight:600}}>{data.doc_embeddings?.[0]?.count ?? '—'}</div>
        <span className='small'>Total rows</span>
      </div>
      <div className='card' style={{gridColumn:'1 / -1'}}>
        <h3 style={{margin:'0 0 .4rem'}}>Runtime Stats ({selectedWindow})</h3>
        <table><thead><tr><th>Metric</th><th>Window</th><th>Count</th><th>Avg</th><th>P50</th><th>P95</th><th>Trend</th></tr></thead>
          <tbody>{data.runtime_stats?.[selectedWindow]?.map(r=>{ const hist=history[r.metric+':'+r.window]||[]; return <tr key={r.metric+r.window}><td>{r.metric}</td><td>{r.window}</td><td>{r.count}</td><td>{r.avg.toFixed(2)}</td><td>{r.p50.toFixed(2)}</td><td>{r.p95.toFixed(2)}</td><td style={{minWidth:120}}><Spark points={hist} /></td></tr>; }) || null}
          {!data.runtime_stats?.[selectedWindow]?.length && <tr><td colSpan={7} style={{fontSize:'.7rem', opacity:.6}}>No metrics</td></tr>}
        </tbody></table>
      </div>
      <div className='card' style={{gridColumn:'1 / -1'}}>
        <h3 style={{margin:'0 0 .4rem'}}>Ingestion Log ({selectedWindow})</h3>
        <ul style={{margin:0,paddingLeft:'1.1rem', fontSize:'.7rem'}}>{data.ingest_log?.[selectedWindow]?.map(r=> <li key={r.status}>{r.status}: {r.count}</li>) || <li>None</li>}</ul>
      </div>
    </div>}
  </div>;
};

export default Dashboard;
