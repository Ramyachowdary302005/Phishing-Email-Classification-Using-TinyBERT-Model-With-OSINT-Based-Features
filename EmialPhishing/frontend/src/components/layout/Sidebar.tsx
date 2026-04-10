import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Settings, Network, History } from 'lucide-react';
import { cn } from '../../utils/cn';

export function Sidebar() {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/analysis', icon: ShieldAlert, label: 'Email Analysis' },
    { to: '/history', icon: History, label: 'History' },
    { to: '/model', icon: Network, label: 'Model Management' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-white dark:bg-dark-card border-r border-gray-200 dark:border-dark-border hidden md:flex flex-col h-screen fixed top-0 left-0">
      <div className="h-16 flex items-center px-6 border-b border-gray-200 dark:border-dark-border">
        <ShieldAlert className="w-8 h-8 text-primary-500 mr-2" />
        <span className="text-xl font-bold text-gray-900 dark:text-white">PhishGuard AI</span>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors group",
                isActive
                  ? "bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-dark-border/50 hover:text-gray-900 dark:hover:text-white"
              )
            }
          >
            <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      {/* Optional: Add user profile / version here */}
    </aside>
  );
}
