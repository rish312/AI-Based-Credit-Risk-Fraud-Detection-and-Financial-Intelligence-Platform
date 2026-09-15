import React, { useContext } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { LayoutDashboard, FileText, CheckSquare, Activity, LogOut } from 'lucide-react';

const Layout = () => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard, roles: ['loan_officer', 'fraud_analyst', 'compliance', 'admin', 'user'] },
    { name: 'New Prediction', path: '/predict', icon: FileText, roles: ['loan_officer', 'fraud_analyst', 'admin'] },
    { name: 'Review Queue', path: '/review', icon: CheckSquare, roles: ['fraud_analyst', 'admin'] },
    { name: 'Monitoring', path: '/monitoring', icon: Activity, roles: ['compliance', 'admin'] },
  ];

  const allowedNavItems = navItems.filter(item => item.roles.includes(user?.role));

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-4 text-xl font-bold border-b border-slate-700 flex items-center space-x-2">
          <Activity className="h-6 w-6 text-blue-400" />
          <span>RiskEngine ML</span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-2">
            {allowedNavItems.map((item) => {
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center space-x-3 px-3 py-2.5 rounded-md transition-colors ${
                    isActive 
                      ? 'bg-blue-600 text-white' 
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                  {item.name === 'Review Queue' && (
                    <span className="ml-auto bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                      3
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 shrink-0">
          <h2 className="text-xl font-semibold text-slate-800">
            {allowedNavItems.find(item => item.path === location.pathname)?.name || 'Platform'}
          </h2>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-right">
              <div className="font-medium text-slate-900">{user?.username}</div>
              <div className="text-slate-500 capitalize">{user?.role?.replace('_', ' ')}</div>
            </div>
            <button 
              onClick={logout}
              className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
