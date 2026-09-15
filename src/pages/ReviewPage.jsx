import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, X, Eye, AlertCircle, FileText, Filter } from 'lucide-react';

const ReviewPage = () => {
  const [activeFilter, setActiveFilter] = useState('Pending');
  
  const [reviews, setReviews] = useState([
    { id: 'PRD-7828', date: '2023-10-25 14:32', amount: 12000, fraudScore: 0.88, tier: 'Manual-Review', status: 'Pending', notes: '' },
    { id: 'PRD-7822', date: '2023-10-25 10:15', amount: 8500, fraudScore: 0.92, tier: 'Manual-Review', status: 'Pending', notes: '' },
    { id: 'PRD-7819', date: '2023-10-24 16:45', amount: 15000, fraudScore: 0.76, tier: 'Manual-Review', status: 'Pending', notes: '' },
    { id: 'PRD-7810', date: '2023-10-24 09:20', amount: 3200, fraudScore: 0.65, tier: 'Manual-Review', status: 'Approved', notes: 'Verified with customer via phone.' },
    { id: 'PRD-7805', date: '2023-10-23 15:10', amount: 9800, fraudScore: 0.85, tier: 'Manual-Review', status: 'Declined', notes: 'Suspicious IP mismatch.' },
  ]);

  const filteredReviews = activeFilter === 'All' 
    ? reviews 
    : reviews.filter(r => r.status === activeFilter);

  const handleAction = (id, action) => {
    setReviews(reviews.map(r => 
      r.id === id ? { ...r, status: action === 'approve' ? 'Approved' : 'Declined' } : r
    ));
  };

  const handleNoteChange = (id, text) => {
    setReviews(reviews.map(r => 
      r.id === id ? { ...r, notes: text } : r
    ));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center">
            Review Queue
            <span className="ml-3 bg-red-100 text-red-800 text-sm font-semibold px-2.5 py-0.5 rounded-full">
              {reviews.filter(r => r.status === 'Pending').length} Pending
            </span>
          </h1>
          <p className="text-slate-500 mt-1">Manual review queue for flagged transactions.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Header / Filters */}
        <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between space-y-3 sm:space-y-0 bg-slate-50">
          <div className="flex space-x-2">
            {['All', 'Pending', 'Approved', 'Declined'].map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeFilter === filter
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white text-slate-600 border border-slate-300 hover:bg-slate-50'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
          <button className="flex items-center text-sm text-slate-500 hover:text-slate-700 bg-white border border-slate-300 px-3 py-1.5 rounded-md">
            <Filter className="w-4 h-4 mr-2" />
            More Filters
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-white">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Prediction ID</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date & Time</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Amount</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Fraud Score</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {filteredReviews.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-10 text-center text-slate-500">
                    <AlertCircle className="mx-auto h-8 w-8 text-slate-300 mb-2" />
                    No reviews found in this category.
                  </td>
                </tr>
              ) : (
                filteredReviews.map((review) => (
                  <React.Fragment key={review.id}>
                    <tr className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <FileText className="w-4 h-4 text-slate-400 mr-2" />
                          <Link to={`/predictions/${review.id}`} className="text-sm font-medium text-blue-600 hover:text-blue-900">
                            {review.id}
                          </Link>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{review.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">${review.amount.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`text-sm font-bold ${review.fraudScore > 0.8 ? 'text-red-600' : 'text-orange-500'}`}>
                            {review.fraudScore.toFixed(2)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          review.status === 'Approved' ? 'bg-green-100 text-green-800' :
                          review.status === 'Declined' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {review.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                        {review.status === 'Pending' ? (
                          <div className="flex justify-center space-x-2">
                            <button 
                              onClick={() => handleAction(review.id, 'approve')}
                              className="p-1.5 bg-green-50 text-green-600 hover:bg-green-100 rounded-md border border-green-200 transition-colors"
                              title="Approve"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => handleAction(review.id, 'decline')}
                              className="p-1.5 bg-red-50 text-red-600 hover:bg-red-100 rounded-md border border-red-200 transition-colors"
                              title="Decline"
                            >
                              <X className="w-4 h-4" />
                            </button>
                            <Link to={`/predictions/${review.id}`} className="p-1.5 bg-slate-50 text-slate-600 hover:bg-slate-100 rounded-md border border-slate-200 transition-colors" title="View Details">
                              <Eye className="w-4 h-4" />
                            </Link>
                          </div>
                        ) : (
                          <Link to={`/predictions/${review.id}`} className="text-blue-600 hover:text-blue-900 font-medium">
                            View
                          </Link>
                        )}
                      </td>
                    </tr>
                    {review.status === 'Pending' && (
                      <tr className="bg-slate-50 border-b-2 border-slate-200">
                        <td colSpan="6" className="px-6 py-3">
                          <input 
                            type="text" 
                            value={review.notes}
                            onChange={(e) => handleNoteChange(review.id, e.target.value)}
                            placeholder="Add review notes here before deciding..."
                            className="w-full text-sm border-slate-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border outline-none"
                          />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ReviewPage;
