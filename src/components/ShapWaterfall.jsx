import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

const ShapWaterfall = ({ baseValue, features, outputValue, title }) => {
  // Sort features by absolute contribution descending
  const sortedFeatures = [...features].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  
  // Take top 10, combine rest
  const topFeatures = sortedFeatures.slice(0, 10);
  const otherFeatures = sortedFeatures.slice(10);
  
  if (otherFeatures.length > 0) {
    const otherContribution = otherFeatures.reduce((sum, f) => sum + f.contribution, 0);
    topFeatures.push({ name: 'Other Features', contribution: otherContribution });
  }

  // Calculate cumulative values for waterfall chart
  let currentVal = baseValue;
  const chartData = topFeatures.map((feature, index) => {
    const startVal = currentVal;
    currentVal += feature.contribution;
    const endVal = currentVal;
    
    // For recharts waterfall, we need an array [min, max]
    const valArray = [startVal, endVal];
    // Sort array so min is first, max is second for the Bar component
    valArray.sort((a, b) => a - b);
    
    return {
      name: feature.name,
      value: valArray,
      contribution: feature.contribution,
      originalStart: startVal,
      originalEnd: endVal,
      isPositive: feature.contribution > 0
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-slate-200 shadow-md rounded-md">
          <p className="font-medium text-slate-800">{data.name}</p>
          <p className={`text-sm ${data.isPositive ? 'text-red-600' : 'text-blue-600'}`}>
            Contribution: {data.contribution > 0 ? '+' : ''}{data.contribution.toFixed(4)}
          </p>
          <p className="text-sm text-slate-500">
            Impact: {data.originalStart.toFixed(4)} → {data.originalEnd.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-80">
      <h3 className="text-center font-medium text-slate-700 mb-4">{title}</h3>
      <div className="flex justify-between text-xs text-slate-500 px-10 mb-2">
        <div>Base Value: <span className="font-bold">{baseValue.toFixed(4)}</span></div>
        <div>Output Value: <span className="font-bold">{outputValue.toFixed(4)}</span></div>
      </div>
      <ResponsiveContainer width="100%" height="80%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" domain={['dataMin - 0.1', 'dataMax + 0.1']} />
          <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x={baseValue} stroke="#94a3b8" strokeDasharray="3 3" />
          <ReferenceLine x={outputValue} stroke="#1e293b" />
          <Bar dataKey="value" barSize={20}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.isPositive ? '#ef4444' : '#3b82f6'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex justify-center space-x-6 mt-4">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
          <span className="text-xs text-slate-600">Increases Score (Red)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
          <span className="text-xs text-slate-600">Decreases Score (Blue)</span>
        </div>
      </div>
    </div>
  );
};

export default ShapWaterfall;
