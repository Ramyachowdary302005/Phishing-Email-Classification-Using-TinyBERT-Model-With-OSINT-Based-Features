import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { api } from '../services/api';
import { HealthResponse } from '../types';
import { ShieldAlert, Cpu, Activity, Database } from 'lucide-react';
import { useHistory } from '../context/HistoryContext';
import { useNavigate } from 'react-router-dom';

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { history } = useHistory();
  const navigate = useNavigate();

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.health();
        setHealth(res);
      } catch (error) {
        console.error("Health check failed", error);
      } finally {
        setLoading(false);
      }
    };
    checkHealth();
  }, []);

  const totalScans = history.length;
  const phishCount = history.filter(h => h.response.final_decision === 'Phishing').length;
  const legCount = totalScans - phishCount;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            System status and recent activity summary.
          </p>
        </div>
        <button
          onClick={() => navigate('/analysis')}
          className="mt-4 md:mt-0 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium shadow-sm transition-colors flex items-center"
        >
          <ShieldAlert className="w-4 h-4 mr-2" />
          New Scan
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Scans</CardTitle>
            <Activity className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalScans}</div>
            <p className="text-xs text-gray-500 mt-1">Local history records</p>
          </CardContent>
        </Card>
        
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-red-600 dark:text-red-400">Phishing Detected</CardTitle>
            <ShieldAlert className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{phishCount}</div>
            <p className="text-xs text-gray-500 mt-1">Malicious emails identified</p>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-green-600 dark:text-green-400">Legitimate</CardTitle>
            <ShieldAlert className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{legCount}</div>
            <p className="text-xs text-gray-500 mt-1">Safe emails identified</p>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Cpu className="h-4 w-4 text-primary-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {loading ? (
                <span className="text-gray-400 text-lg animate-pulse">Checking...</span>
              ) : health?.status === 'ok' ? 'Online' : 'Offline'}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Backend API connection {health?.version && `v${health.version}`}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
         {/* Recent Activity Mini-Widget */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="text-center py-6 text-gray-500">No recent scans.</div>
            ) : (
              <div className="space-y-4">
                {history.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3 last:border-0">
                    <div className="flex flex-col truncate pr-4">
                      <span className="font-medium text-sm truncate">{item.request.headers.from}</span>
                      <span className="text-xs text-gray-500">{new Date(item.date).toLocaleString()}</span>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs font-semibold ${item.response.final_decision === 'Phishing' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'}`}>
                      {item.response.final_decision}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Backend Status Widget */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Model Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                 <div className="flex items-center text-sm font-medium">
                   <Database className="w-4 h-4 mr-2 text-primary-500"/>
                   TinyBERT Classifier
                 </div>
                 <span className="text-xs bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-300 px-2 py-0.5 rounded">Active</span>
              </div>
              <div className="flex items-center justify-between">
                 <div className="flex items-center text-sm font-medium">
                   <ShieldAlert className="w-4 h-4 mr-2 text-primary-500"/>
                   OSINT Analyzer
                 </div>
                 <span className="text-xs bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-300 px-2 py-0.5 rounded">Active</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
