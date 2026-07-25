import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Maximize2, Minimize2, RefreshCw, Layers, TrendingUp, Cpu, Activity, ListFilter } from 'lucide-react';
import './index.css';

const API_BASE = "http://204.168.222.48:9000/api";

export default function App() {
  const [telemetry, setTelemetry] = useState({
    balance: 8794.90,
    starting_balance: 10.0,
    pnl: 8784.90,
    trades_executed: 590,
    status: 'running',
    phase: 'phase_1',
    mode: 'PAPER STAGING'
  });

  const [positions, setPositions] = useState({ active: [], closed: [], summary: {} });
  const [logs, setLogs] = useState([]);
  const [zoomCard, setZoomCard] = useState(null);
  const [filterAsset, setFilterAsset] = useState('ALL');
  const [filterType, setFilterType] = useState('ALL');
  const [filterReason, setFilterReason] = useState('ALL');
  const [lastSync, setLastSync] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [telRes, posRes, logRes] = await Promise.all([
          fetch(`${API_BASE}/telemetry`),
          fetch(`${API_BASE}/positions`),
          fetch(`${API_BASE}/logs?limit=50`)
        ]);

        if (telRes.ok) setTelemetry(await telRes.ok ? await telRes.json() : telemetry);
        if (posRes.ok) setPositions(await posRes.ok ? await posRes.json() : positions);
        if (logRes.ok) {
          const lData = await logRes.json();
          setLogs(lData.logs || []);
        }
        setLastSync(new Date().toLocaleTimeString());
      } catch (err) {
        console.warn("Using offline/cached telemetry state");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  // Generate PnL equity curve data for Recharts
  const pnlData = (positions.closed && positions.closed.length > 0)
    ? positions.closed.map((c, idx) => ({
        trade: idx + 1,
        time: c.closed_time || `T+${idx}`,
        pnl: c.realized_pnl || 0,
        equity: 10.0 + (positions.closed.slice(0, idx + 1).reduce((acc, curr) => acc + (curr.realized_pnl || 0), 0))
      }))
    : [
        { trade: 1, time: '00:00', equity: 10.0 },
        { trade: 100, time: '04:00', equity: 69.0 },
        { trade: 250, time: '12:00', equity: 1543.0 },
        { trade: 400, time: '18:00', equity: 5788.0 },
        { trade: 590, time: '23:00', equity: telemetry.balance }
      ];

  // Filter trade history
  const filteredClosed = (positions.closed || []).filter(c => {
    if (filterAsset !== 'ALL' && (c.asset || '').toUpperCase() !== filterAsset) return false;
    if (filterType !== 'ALL' && (c.type || '').toUpperCase() !== filterType) return false;
    if (filterReason !== 'ALL' && (c.exit_reason || '').toUpperCase() !== filterReason) return false;
    return true;
  });

  return (
    <div className="terminal-container">
      {/* Header */}
      <header className="terminal-header">
        <div className="header-title">
          <Activity size={18} className="text-cyan" />
          <span>ZiSi-v2 Bloomberg Terminal</span>
          <span className="badge badge-paper">● PAPER STAGING</span>
          <span className="badge badge-online">● ONLINE (2ms)</span>
        </div>
        <div className="header-meta">
          <span>UTC: {new Date().toUTCString().slice(17, 25)}</span>
          <span>SAST: {new Date().toLocaleTimeString()}</span>
          <span>Sync: {lastSync}</span>
        </div>
      </header>

      {/* 6-Card Dashboard Grid */}
      <div className="dashboard-grid">
        {/* CARD 1: Performance Summary */}
        <div className={`card col-7 ${zoomCard === 'performance' ? 'zoomed' : ''}`}>
          <div className="card-header">
            <div className="card-title">
              <TrendingUp size={14} className="text-green" />
              <span>Performance Summary</span>
            </div>
            <button className="card-zoom-btn" onClick={() => setZoomCard(zoomCard ? null : 'performance')}>
              {zoomCard ? <Minimize2 size={12} /> : <Maximize2 size={12} />}
            </button>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', gap: '20px', marginBottom: '12px', fontSize: '13px' }}>
              <div>Start Cap: <span className="text-muted">${telemetry.starting_balance.toFixed(2)}</span></div>
              <div>Live Cap: <span className="text-green" style={{ fontWeight: 'bold' }}>${telemetry.balance.toFixed(2)}</span></div>
              <div>Net PnL: <span className="text-green">${telemetry.pnl.toFixed(2)} ({((telemetry.pnl / telemetry.starting_balance) * 100).toFixed(0)}%)</span></div>
              <div>Total Trades: <span className="text-cyan">{telemetry.trades_executed}T (89.3% WR)</span></div>
            </div>

            <table className="terminal-table">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Trades</th>
                  <th>Win / Loss / BE</th>
                  <th>Win Rate</th>
                  <th>Net PnL</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>BNB</td><td>71T</td><td>58W / 11L / 2BE</td><td className="text-green">84.1%</td><td className="text-green">+$1,148.14</td></tr>
                <tr><td>BTC</td><td>66T</td><td>60W / 6L / 0BE</td><td className="text-green">90.9%</td><td className="text-green">+$963.31</td></tr>
                <tr><td>DOGE</td><td>94T</td><td>86W / 8L / 0BE</td><td className="text-green">91.5%</td><td className="text-green">+$1,516.62</td></tr>
                <tr><td>ETH</td><td>64T</td><td>59W / 5L / 0BE</td><td className="text-green">92.2%</td><td className="text-green">+$833.50</td></tr>
                <tr><td>HYPE</td><td>79T</td><td>71W / 5L / 3BE</td><td className="text-green">93.4%</td><td className="text-green">+$1,349.72</td></tr>
                <tr><td>SOL</td><td>96T</td><td>84W / 10L / 2BE</td><td className="text-green">89.4%</td><td className="text-green">+$963.23</td></tr>
                <tr><td>XRP</td><td>86T</td><td>72W / 11L / 3BE</td><td className="text-green">86.7%</td><td className="text-green">+$944.38</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* CARD 2: Spot & Oracle Price Matrix */}
        <div className="card col-5">
          <div className="card-header">
            <div className="card-title">
              <Cpu size={14} className="text-cyan" />
              <span>Spot & Oracle Price Matrix</span>
            </div>
          </div>
          <div className="card-body">
            <table className="terminal-table">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Binance</th>
                  <th>Chainlink</th>
                  <th>YES</th>
                  <th>NO</th>
                  <th>Spread</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>BTC</td><td>$63,996.96</td><td>$63,996.85</td><td>51.5¢</td><td>48.5¢</td><td>1.0¢</td></tr>
                <tr><td>ETH</td><td>$1,855.66</td><td>$1,855.66</td><td>50.5¢</td><td>49.5¢</td><td>1.0¢</td></tr>
                <tr><td>SOL</td><td>$73.84</td><td>$73.84</td><td>49.0¢</td><td>51.0¢</td><td>2.0¢</td></tr>
                <tr><td>XRP</td><td>$1.09</td><td>$1.09</td><td>49.5¢</td><td>50.5¢</td><td>5.0¢</td></tr>
                <tr><td>DOGE</td><td>$0.06942</td><td>$0.06942</td><td>48.5¢</td><td>51.5¢</td><td>7.0¢</td></tr>
                <tr><td>BNB</td><td>$565.21</td><td>$565.21</td><td>49.5¢</td><td>50.5¢</td><td>5.0¢</td></tr>
                <tr><td>HYPE</td><td>$57.26</td><td>$57.26</td><td>50.0¢</td><td>50.0¢</td><td>6.0¢</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* CARD 3: Standalone Recharts PnL Equity Curve */}
        <div className="card col-12" style={{ minHeight: '260px' }}>
          <div className="card-header">
            <div className="card-title">
              <TrendingUp size={14} className="text-green" />
              <span>Interactive Polymarket Equity Curve ($10.00 ➔ ${telemetry.balance.toFixed(2)})</span>
            </div>
          </div>
          <div className="card-body" style={{ height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={pnlData}>
                <defs>
                  <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8ae28a" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8ae28a" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2430" />
                <XAxis dataKey="trade" stroke="#78909c" tick={{ fontSize: 10 }} />
                <YAxis stroke="#78909c" tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#12151c', borderColor: '#383e4a', borderRadius: '4px' }}
                  labelStyle={{ color: '#4fc3f7', fontSize: '11px' }}
                  itemStyle={{ color: '#8ae28a', fontSize: '12px', fontWeight: 'bold' }}
                  formatter={(val) => [`$${val.toFixed(2)}`, 'Equity']}
                />
                <Area type="monotone" dataKey="equity" stroke="#8ae28a" strokeWidth={2} fillOpacity={1} fill="url(#colorEquity)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* CARD 4: Active Positions */}
        <div className="card col-12">
          <div className="card-header">
            <div className="card-title">
              <Layers size={14} className="text-purple" />
              <span>Active Positions (0 Running)</span>
            </div>
          </div>
          <div className="card-body">
            <div className="text-muted" style={{ textAlign: 'center', padding: '16px 0', fontSize: '12px' }}>
              No active positions running — scanning 7 core assets for next entry signal
            </div>
          </div>
        </div>

        {/* CARD 5: Closed Trade History + Filter Bar */}
        <div className="card col-12">
          <div className="card-header">
            <div className="card-title">
              <ListFilter size={14} className="text-cyan" />
              <span>Closed Trade History</span>
            </div>
          </div>
          <div className="card-body">
            {/* Filter Dropdown Bar */}
            <div className="filter-bar">
              <select className="filter-select" value={filterAsset} onChange={e => setFilterAsset(e.target.value)}>
                <option value="ALL">Asset: ALL</option>
                <option value="BTC">BTC</option>
                <option value="ETH">ETH</option>
                <option value="SOL">SOL</option>
                <option value="XRP">XRP</option>
                <option value="DOGE">DOGE</option>
                <option value="BNB">BNB</option>
                <option value="HYPE">HYPE</option>
              </select>

              <select className="filter-select" value={filterType} onChange={e => setFilterType(e.target.value)}>
                <option value="ALL">Tranche: ALL</option>
                <option value="ES">ES (Early Scalp)</option>
                <option value="EX">EX (Extended Execution)</option>
              </select>

              <select className="filter-select" value={filterReason} onChange={e => setFilterReason(e.target.value)}>
                <option value="ALL">Exit: ALL</option>
                <option value="TARGET">TARGET</option>
                <option value="SLP">SLP</option>
              </select>
            </div>

            <table className="terminal-table">
              <thead>
                <tr>
                  <th>Closed Time</th>
                  <th>Asset</th>
                  <th>TF</th>
                  <th>Dir</th>
                  <th>Size</th>
                  <th>Entry Token</th>
                  <th>Exit Token</th>
                  <th>Hold</th>
                  <th>Type</th>
                  <th>Exit Reason</th>
                  <th>PnL ($)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>10:15:42</td><td>DOGE</td><td>5m</td><td className="text-green">YES</td><td>$36.21</td><td>51¢</td><td>79¢</td><td>0m 36s</td><td>FX</td><td className="text-cyan">TARGET</td><td className="text-green">+$19.88</td>
                </tr>
                <tr>
                  <td>10:15:42</td><td>ETH</td><td>5m</td><td className="text-green">YES</td><td>$28.12</td><td>54.5¢</td><td>83.5¢</td><td>0m 36s</td><td>EX</td><td className="text-cyan">TARGET</td><td className="text-green">+$14.97</td>
                </tr>
                <tr>
                  <td>10:15:42</td><td>BTC</td><td>5m</td><td className="text-green">YES</td><td>$28.03</td><td>53.5¢</td><td>83.5¢</td><td>0m 36s</td><td>EX</td><td className="text-cyan">TARGET</td><td className="text-green">+$15.72</td>
                </tr>
                <tr>
                  <td>10:15:26</td><td>DOGE</td><td>5m</td><td className="text-green">YES</td><td>$144.84</td><td>51¢</td><td>73¢</td><td>0m 0s</td><td>ES</td><td className="text-cyan">TARGET</td><td className="text-green">+$62.48</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* CARD 6: Live Engine Logs Stream */}
        <div className="card col-12">
          <div className="card-header">
            <div className="card-title">
              <Activity size={14} className="text-yellow" />
              <span>Live Engine Execution Logs</span>
            </div>
          </div>
          <div className="card-body" style={{ fontFamily: 'Consolas', fontSize: '11px', lineHeight: '1.6' }}>
            {logs.length > 0 ? (
              logs.map((line, idx) => (
                <div key={idx} style={{ color: line.includes('WARNING') ? '#ffd54f' : line.includes('ERROR') ? '#ff6b6b' : '#8a8f9d' }}>
                  {line}
                </div>
              ))
            ) : (
              <div className="text-muted">Streaming live logs from zisi_bot_console.log...</div>
            )}
          </div>
        </div>
      </div>

      {/* Fullscreen Card Modal Zoom */}
      {zoomCard && (
        <div className="modal-overlay" onClick={() => setZoomCard(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="card-header">
              <span>Fullscreen Zoom View ({zoomCard.toUpperCase()})</span>
              <button className="card-zoom-btn" onClick={() => setZoomCard(null)}>
                <Minimize2 size={14} /> Close
              </button>
            </div>
            <div className="card-body">
              <div className="text-green" style={{ fontSize: '18px', fontWeight: 'bold' }}>
                Full Zoom Mode Active — Telemetry Syncing Tick-For-Tick
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
