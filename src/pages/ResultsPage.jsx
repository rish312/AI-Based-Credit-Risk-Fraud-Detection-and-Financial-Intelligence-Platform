import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, ShieldCheck, UserCheck, Calendar } from 'lucide-react';
import ShapWaterfall from '../components/ShapWaterfall';

const ResultsPage = () => {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('credit');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setData({
        id: id || 'PRD-7830',
        timestamp: new Date().toISOString(),
        models: {
          credit: 'v2.1.4',
          fraud: 'v1.8.0',
          segmentation: 'v3.0.2'
        },
        credit: {
          score: 0.82,
          probability: 0.15,
          tier: 'High', // Low, Medium, High, Very High
          shap: {
            baseValue: 0.45,
            outputValue: 0.82,
            features: [
              { name: 'Credit Score', value: 620, contribution: 0.15 },
              { name: 'Existing Debt', value: 45000, contribution: 0.12 },
              { name: 'Income', value: 55000, contribution: 0.08 },
              { name: 'Employment Years', value: 2, contribution: 0.05 },
              { name: 'Age', value: 28, contribution: -0.03 },
            ]
          }
        },
        fraud: {
          score: 0.65,
          decision: 'Manual Review', // Auto-Approve, Manual Review, Auto-Decline
          shap: {
            baseValue: 0.10,
            outputValue: 0.65,
            features: [
              { name: 'Transaction Amount', value: 4500, contribution: 0.25 },
              { name: 'IP Country', value: 'RU', contribution: 0.18 },
              { name: 'Device Age', value: 1, contribution: 0.08 },
              { name: 'Hour of Day', value: 3, contribution: 0.06 },
              { name: 'Prior Transactions', value: 50, contribution: -0.02 },
            ]
          }
        },
        segmentation: {
          segment: 'Occasional Big Spender',
          confidence: 88,
          description: 'Users who purchase rarely but spend significantly above average when they do.',
          color: 'bg-purple-100 text-purple-800'
        }
      });
      setLoading(false);
    }, 1000);
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const getTierColor = (tier) => {
    switch (tier) {
      case 'Low': return 'text-green-600 bg-green-50 border-green-200';
      case 'Medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'High': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'Very High': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-slate-600 bg-slate-50 border-slate-200';
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'Auto-Approve': return 'text-green-600 bg-green-50 border-green-200';
      case 'Manual Review': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Auto-Decline': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-slate-600 bg-slate-50 border-slate-200';
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/" className="p-2 bg-white border border-slate-200 rounded-md shadow-sm hover:bg-slate-50 text-slate-500">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Prediction Results</h1>
            <p className="text-slate-500 text-sm">ID: {data.id}</p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Credit Risk Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center text-center">
          <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mb-4">
            <AlertTriangle className="w-6 h-6 text-blue-600" />
          </div>
          <h2 className="text-lg font-semibold text-slate-800">Credit Risk</h2>
          
          <div className="mt-4 relative">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-slate-100" />
              <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - data.credit.score)}`}
                className={`${data.credit.score > 0.7 ? 'text-red-500' : data.credit.score > 0.4 ? 'text-orange-500' : 'text-green-500'}`}
              />
            </svg>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="text-2xl font-bold text-slate-800">{data.credit.score.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="mt-6 flex flex-col space-y-2 w-full">
            <div className="flex justify-between items-center border-b border-slate-100 pb-2">
              <span className="text-sm text-slate-500">Risk Tier</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getTierColor(data.credit.tier)}`}>
                {data.credit.tier}
              </span>
            </div>
            <div className="flex justify-between items-center pb-2">
              <span className="text-sm text-slate-500">Calibrated Prob.</span>
              <span className="text-sm font-medium text-slate-800">{(data.credit.probability * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Fraud Detection Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center text-center">
          <div className="w-12 h-12 bg-purple-50 rounded-full flex items-center justify-center mb-4">
            <ShieldCheck className="w-6 h-6 text-purple-600" />
          </div>
          <h2 className="text-lg font-semibold text-slate-800">Fraud Detection</h2>
          
          <div className="mt-4 relative">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-slate-100" />
              <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - data.fraud.score)}`}
                className={`${data.fraud.score > 0.8 ? 'text-red-500' : data.fraud.score > 0.5 ? 'text-yellow-500' : 'text-green-500'}`}
              />
            </svg>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="text-2xl font-bold text-slate-800">{data.fraud.score.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="mt-6 flex flex-col space-y-2 w-full">
            <div className="flex justify-between items-center border-b border-slate-100 pb-2">
              <span className="text-sm text-slate-500">Decision</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getDecisionColor(data.fraud.decision)}`}>
                {data.fraud.decision}
              </span>
            </div>
          </div>
        </div>

        {/* Customer Segment Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center text-center justify-between">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-teal-50 rounded-full flex items-center justify-center mb-4">
              <UserCheck className="w-6 h-6 text-teal-600" />
            </div>
            <h2 className="text-lg font-semibold text-slate-800 mb-6">Customer Segment</h2>
            
            <span className={`px-4 py-2 rounded-lg text-sm font-bold mb-4 ${data.segmentation.color}`}>
              {data.segmentation.segment}
            </span>
            
            <p className="text-sm text-slate-600 px-2 italic">
              "{data.segmentation.description}"
            </p>
          </div>
          
          <div className="mt-6 w-full flex justify-between items-center pt-4 border-t border-slate-100">
            <span className="text-sm text-slate-500">Confidence Match</span>
            <span className="text-sm font-bold text-teal-600">{data.segmentation.confidence}%</span>
          </div>
        </div>
      </div>

      {/* SHAP Explanations */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <h2 className="text-lg font-medium text-slate-800">Model Explanations (SHAP)</h2>
        </div>
        
        <div className="border-b border-slate-200">
          <nav className="flex -mb-px px-6">
            <button
              onClick={() => setActiveTab('credit')}
              className={`whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'credit'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              Credit Risk Model
            </button>
            <button
              onClick={() => setActiveTab('fraud')}
              className={`whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'fraud'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              Fraud Detection Model
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'credit' && (
            <ShapWaterfall
              baseValue={data.credit.shap.baseValue}
              features={data.credit.shap.features}
              outputValue={data.credit.shap.outputValue}
              title="Feature Contributions to Credit Risk Score"
            />
          )}
          
          {activeTab === 'fraud' && (
            <ShapWaterfall
              baseValue={data.fraud.shap.baseValue}
              features={data.fraud.shap.features}
              outputValue={data.fraud.shap.outputValue}
              title="Feature Contributions to Fraud Score"
            />
          )}
        </div>
      </div>

      {/* Metadata Footer */}
      <div className="text-xs text-slate-400 flex items-center justify-between pb-8">
        <div className="flex items-center">
          <Calendar className="w-3 h-3 mr-1" />
          Predicted at: {new Date(data.timestamp).toLocaleString()}
        </div>
        <div className="flex space-x-4">
          <span>Credit: {data.models.credit}</span>
          <span>Fraud: {data.models.fraud}</span>
          <span>Seg: {data.models.segmentation}</span>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
