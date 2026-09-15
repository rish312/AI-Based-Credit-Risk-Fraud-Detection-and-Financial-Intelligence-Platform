import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play } from 'lucide-react';
import apiClient from '../api/client';

const PredictPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    // Credit Risk
    income: '',
    employment_years: '',
    existing_debt: '',
    credit_score: '',
    // Fraud
    transaction_amount: '',
    merchant_category: 'retail',
    device_id: '',
    ip_country: 'US',
    hour_of_day: '12',
    // Segmentation
    days_since_last_purchase: '',
    purchase_frequency: '',
    total_spend: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const fillSampleData = (section) => {
    if (section === 'credit') {
      setFormData(prev => ({ ...prev, income: 75000, employment_years: 5, existing_debt: 12000, credit_score: 720 }));
    } else if (section === 'fraud') {
      setFormData(prev => ({ ...prev, transaction_amount: 1500, merchant_category: 'electronics', device_id: 'DEV-9923', ip_country: 'US', hour_of_day: '23' }));
    } else if (section === 'segmentation') {
      setFormData(prev => ({ ...prev, days_since_last_purchase: 15, purchase_frequency: 12, total_spend: 4500 }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      setLoading(false);
      navigate('/predictions/PRD-7830');
    }, 1500);
    
    /* In a real app:
    try {
      const response = await apiClient.post('/predict', formData);
      navigate(`/predictions/${response.data.id}`);
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
    */
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">New Prediction</h1>
        <p className="text-slate-500 mt-1">Enter customer and transaction details to run the ML models.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        
        {/* Credit Risk Section */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
            <h2 className="text-lg font-medium text-slate-800">Credit Risk Profile</h2>
            <button type="button" onClick={() => fillSampleData('credit')} className="text-sm text-blue-600 hover:text-blue-800 font-medium">Fill Sample Data</button>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Annual Income ($)</label>
              <input type="number" name="income" value={formData.income} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Employment Years</label>
              <input type="number" name="employment_years" value={formData.employment_years} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Existing Debt ($)</label>
              <input type="number" name="existing_debt" value={formData.existing_debt} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Credit Score</label>
              <input type="number" name="credit_score" value={formData.credit_score} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
          </div>
        </div>

        {/* Fraud Section */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
            <h2 className="text-lg font-medium text-slate-800">Transaction Details (Fraud)</h2>
            <button type="button" onClick={() => fillSampleData('fraud')} className="text-sm text-blue-600 hover:text-blue-800 font-medium">Fill Sample Data</button>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Transaction Amount ($)</label>
              <input type="number" name="transaction_amount" value={formData.transaction_amount} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Merchant Category</label>
              <select name="merchant_category" value={formData.merchant_category} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none">
                <option value="retail">Retail</option>
                <option value="electronics">Electronics</option>
                <option value="travel">Travel</option>
                <option value="food">Food & Dining</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Device ID</label>
              <input type="text" name="device_id" value={formData.device_id} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">IP Country</label>
              <input type="text" name="ip_country" value={formData.ip_country} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Hour of Day (0-23)</label>
              <input type="number" min="0" max="23" name="hour_of_day" value={formData.hour_of_day} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
          </div>
        </div>

        {/* Segmentation Section */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
            <h2 className="text-lg font-medium text-slate-800">Behavioral Data (Segmentation)</h2>
            <button type="button" onClick={() => fillSampleData('segmentation')} className="text-sm text-blue-600 hover:text-blue-800 font-medium">Fill Sample Data</button>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Days Since Last Purchase</label>
              <input type="number" name="days_since_last_purchase" value={formData.days_since_last_purchase} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Purchase Frequency (per year)</label>
              <input type="number" name="purchase_frequency" value={formData.purchase_frequency} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Total Historical Spend ($)</label>
              <input type="number" name="total_spend" value={formData.total_spend} onChange={handleInputChange} className="w-full rounded-md border border-slate-300 py-2 px-3 shadow-sm focus:border-blue-500 focus:ring-blue-500 outline-none" required />
            </div>
          </div>
        </div>

        <div className="flex justify-end pb-8">
          <button
            type="submit"
            disabled={loading}
            className={`inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running Models...
              </span>
            ) : (
              <span className="flex items-center">
                <Play className="-ml-1 mr-2 h-5 w-5" />
                Run Predictions
              </span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PredictPage;
