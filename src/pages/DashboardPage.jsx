import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { FileText, CheckSquare, AlertTriangle, Users, ArrowRight } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, trend, colorClass }) => (
  <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center">
    <div className={`p-4 rounded-lg ${colorClass} mr-4`}>
      <Icon className="h-6 w-6 text-white" />
    </div>
    <div>
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <div className="flex items-baseline mt-1">
        <h3 className="text-2xl font-bold text-slate-800">{value}</h3>
        {trend && (
          <span className={`ml-2 text-sm font-medium ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
    </div>
  </div>
);

const DashboardPage = () => {
  const { user } = useContext(AuthContext);
  const [stats, setStats] = useState({
    totalPredictions: 142,
    pendingReviews: 12,
    avgRiskScore: 0.24,
    avgFraudScore: 0.11,
  });
  const [recentPredictions, setRecentPredictions] = useState([]);

  useEffect(() => {
    // In a real app, fetch these from API
    // apiClient.get('/stats').then(...)
    setRecentPredictions([
      { id: 'PRD-7829', date: '2023-10-25', amount: 4500, riskTier: 'Low', fraudDecision: 'Auto-Approve', status: 'Completed' },
      { id: 'PRD-7828', date: '2023-10-25', amount: 12000, riskTier: 'High', fraudDecision: 'Manual-Review', status: 'Pending' },
      { id: 'PRD-7827', date: '2023-10-24', amount: 350, riskTier: 'Low', fraudDecision: 'Auto-Approve', status: 'Completed' },
      { id: 'PRD-7826', date: '2023-10-24', amount: 28000, riskTier: 'Very High', fraudDecision: 'Auto-Decline', status: 'Declined' },
      { id: 'PRD-7825', date: '2023-10-24', amount: 1500, riskTier: 'Medium', fraudDecision: 'Auto-Approve', status: 'Completed' },
    ]);
  }, []);

  const getRiskBadgeColor = (tier) => {
    switch(tier) {
      case 'Low': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-orange-100 text-orange-800';
      case 'Very High': return 'bg-red-100 text-red-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  const getFraudBadgeColor = (decision) => {
    switch(decision) {
      case 'Auto-Approve': return 'bg-green-100 text-green-800';
      case 'Manual-Review': return 'bg-yellow-100 text-yellow-800';
      case 'Auto-Decline': return 'bg-red-100 text-red-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Welcome back, {user?.username}</h1>
          <p className="text-slate-500 mt-1">Here's an overview of the platform's activity today.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          {['loan_officer', 'fraud_analyst', 'admin'].includes(user?.role) && (
            <Link to="/predict" className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <FileText className="-ml-1 mr-2 h-5 w-5" />
              New Prediction
            </Link>
          )}
          {['fraud_analyst', 'admin'].includes(user?.role) && (
            <Link to="/review" className="inline-flex items-center px-4 py-2 border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <CheckSquare className="-ml-1 mr-2 h-5 w-5 text-slate-500" />
              Review Queue
            </Link>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Predictions" value={stats.totalPredictions} icon={FileText} trend={12} colorClass="bg-blue-500" />
        <StatCard title="Pending Reviews" value={stats.pendingReviews} icon={CheckSquare} trend={-5} colorClass="bg-yellow-500" />
        <StatCard title="Avg Risk Score" value={stats.avgRiskScore.toFixed(2)} icon={AlertTriangle} trend={2} colorClass="bg-orange-500" />
        <StatCard title="Avg Fraud Score" value={stats.avgFraudScore.toFixed(2)} icon={Users} trend={-1} colorClass="bg-purple-500" />
      </div>

      {/* Recent Activity Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-medium text-slate-900">Recent Predictions</h2>
          <Link to="/predictions/all" className="text-sm font-medium text-blue-600 hover:text-blue-500 flex items-center">
            View all <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">ID</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Amount</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Risk Tier</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Fraud Decision</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="relative px-6 py-3"><span className="sr-only">View</span></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {recentPredictions.map((pred) => (
                <tr key={pred.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{pred.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{pred.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">${pred.amount.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskBadgeColor(pred.riskTier)}`}>
                      {pred.riskTier}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getFraudBadgeColor(pred.fraudDecision)}`}>
                      {pred.fraudDecision}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{pred.status}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link to={`/predictions/${pred.id}`} className="text-blue-600 hover:text-blue-900">View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
