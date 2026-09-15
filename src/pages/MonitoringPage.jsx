import React, { useState } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend, ReferenceLine
} from 'recharts';
import { AlertTriangle, Clock, Activity, CheckCircle2, ServerCrash } from 'lucide-react';

const MonitoringPage = () => {
  const [timeWindow, setTimeWindow] = useState('24h');

  // Mock data for latency
  const latencyData = [
    { time: '00:00', p50: 120, p95: 250, p99: 450 },
    { time: '04:00', p50: 115, p95: 240, p99: 420 },
    { time: '08:00', p50: 140, p95: 280, p99: 550 },
    { time: '12:00', p50: 160, p95: 350, p99: 800 },
    { time: '16:00', p50: 155, p95: 320, p99: 750 },
    { time: '20:00', p50: 130, p95: 260, p99: 480 },
    { time: '24:00', p50: 125, p95: 255, p99: 460 },
  ];

  // Mock data for score distributions
  const creditScoreDist = [
    { range: '0.0-0.2', count: 120 },
    { range: '0.2-0.4', count: 250 },
    { range: '0.4-0.6', count: 380 },
    { range: '0.6-0.8', count: 150 },
    { range: '0.8-1.0', count: 60 },
  ];

  const driftAlerts = [
    { id: 1, feature: 'income', model: 'Credit Risk', driftScore: 0.15, status: 'Warning', time: '2 hours ago' },
    { id: 2, feature: 'transaction_amount', model: 'Fraud', driftScore: 0.22, status: 'Critical', time: '5 hours ago' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">System Monitoring</h1>
          <p className="text-slate-500 mt-1">Platform performance, model drift, and queue metrics.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex bg-slate-200 p-1 rounded-lg">
          {['1h', '6h', '24h', '7d'].map((tw) => (
            <button
              key={tw}
              onClick={() => setTimeWindow(tw)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                timeWindow === tw ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              {tw}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Latency Panel */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-slate-800 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-slate-500" /> API Latency (ms)
            </h2>
            <span className="flex items-center text-sm text-green-600 bg-green-50 px-2 py-1 rounded-md border border-green-200">
              <CheckCircle2 className="w-4 h-4 mr-1" /> Healthy
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={latencyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                <Line type="monotone" dataKey="p50" stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="p95" stroke="#f59e0b" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="p99" stroke="#ef4444" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distributions Panel */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-slate-800 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-slate-500" /> Score Distribution
            </h2>
            <select className="text-sm border-slate-300 rounded-md py-1 pl-2 pr-8 focus:ring-blue-500 focus:border-blue-500">
              <option>Credit Risk Model</option>
              <option>Fraud Model</option>
            </select>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={creditScoreDist} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <RechartsTooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Drift Alerts */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-slate-800 flex items-center">
              <ServerCrash className="w-5 h-5 mr-2 text-slate-500" /> Data Drift Alerts
            </h2>
          </div>
          <div className="space-y-4">
            {driftAlerts.map(alert => (
              <div key={alert.id} className="flex items-start p-4 rounded-lg border border-slate-100 bg-slate-50">
                <AlertTriangle className={`w-5 h-5 mr-3 mt-0.5 ${alert.status === 'Critical' ? 'text-red-500' : 'text-yellow-500'}`} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-slate-900">{alert.feature}</h4>
                    <span className="text-xs text-slate-500">{alert.time}</span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1">
                    Drift detected in <span className="font-semibold">{alert.model}</span> model. 
                    Score: <span className="font-mono">{alert.driftScore}</span>
                  </p>
                </div>
              </div>
            ))}
            {driftAlerts.length === 0 && (
              <div className="text-center py-8 text-slate-500">No drift alerts detected.</div>
            )}
          </div>
        </div>

        {/* Queue Stats */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-slate-800 flex items-center">
              <CheckCircle2 className="w-5 h-5 mr-2 text-slate-500" /> Review Queue Stats
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-4 h-[calc(100%-2rem)]">
            <div className="bg-blue-50 rounded-lg p-4 flex flex-col justify-center items-center text-center border border-blue-100">
              <span className="text-sm font-medium text-blue-800 mb-1">Avg Resolution Time</span>
              <span className="text-3xl font-bold text-blue-900">4.2h</span>
              <span className="text-xs text-blue-600 mt-2">↓ 12% from last week</span>
            </div>
            <div className="bg-green-50 rounded-lg p-4 flex flex-col justify-center items-center text-center border border-green-100">
              <span className="text-sm font-medium text-green-800 mb-1">Auto-Approval Rate</span>
              <span className="text-3xl font-bold text-green-900">78%</span>
              <span className="text-xs text-green-600 mt-2">Target: &gt;75%</span>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 flex flex-col justify-center items-center text-center border border-yellow-100">
              <span className="text-sm font-medium text-yellow-800 mb-1">Manual Review Rate</span>
              <span className="text-3xl font-bold text-yellow-900">18%</span>
              <span className="text-xs text-yellow-600 mt-2">Target: &lt;20%</span>
            </div>
            <div className="bg-red-50 rounded-lg p-4 flex flex-col justify-center items-center text-center border border-red-100">
              <span className="text-sm font-medium text-red-800 mb-1">Auto-Decline Rate</span>
              <span className="text-3xl font-bold text-red-900">4%</span>
              <span className="text-xs text-red-600 mt-2">Stable</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default MonitoringPage;
