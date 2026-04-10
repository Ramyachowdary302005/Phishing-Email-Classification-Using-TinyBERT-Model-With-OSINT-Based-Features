import React from 'react';
import { Moon, Sun, Menu, LogOut } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../common/Button';

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  // Get initials from user name
  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : 'AD';

  return (
    <header className="h-16 bg-white/80 dark:bg-dark-card/80 backdrop-blur-md border-b border-gray-200 dark:border-dark-border sticky top-0 z-10">
      <div className="h-full px-4 flex items-center justify-between xl:px-8">
        <div className="flex items-center">
          <Button variant="ghost" className="md:hidden mr-2 px-2" onClick={onMenuClick}>
            <Menu className="w-5 h-5" />
          </Button>
          <div className="md:hidden flex items-center font-bold text-lg dark:text-white">
            PhishGuard AI
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="w-10 h-10 rounded-full p-0"
            title="Toggle theme"
          >
            {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          </Button>

          {/* User info */}
          {user && (
            <div className="hidden sm:flex items-center space-x-2">
              <div className="text-right">
                <div className="text-xs font-semibold text-gray-800 dark:text-gray-200 leading-none">{user.name}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{user.role}</div>
              </div>
            </div>
          )}

          {/* Avatar */}
          <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-700 dark:text-primary-300 font-semibold text-sm select-none">
            {initials}
          </div>

          {/* Logout */}
          <Button
            variant="ghost"
            size="sm"
            onClick={logout}
            className="w-9 h-9 rounded-full p-0 text-gray-500 hover:text-red-500 dark:hover:text-red-400"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
