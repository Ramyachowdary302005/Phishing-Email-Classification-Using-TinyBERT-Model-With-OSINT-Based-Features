import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { api } from '../services/api';
import { Thresholds } from '../types';
import { Settings2 } from 'lucide-react';

export function Settings() {
  const [thresholds, setThresholds] = useState<Thresholds>({
    ml_confidence_threshold: 0.8,
    osint_risk_threshold: 0.6,
    hybrid_weight_ml: 0.5,
    hybrid_weight_osint: 0.5,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error', msg: string } | null>(null);

  useEffect(() => {
    const loadSettings = async () => {
      setLoading(true);
      try {
        const res = await api.getThresholds();
        setThresholds(res);
      } catch (err) {
        console.error("Failed to load thresholds", err);
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, []);

  const handleChange = (key: keyof Thresholds, value: number) => {
    setThresholds((prev: Thresholds) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setNotification(null);
    try {
      await api.updateThresholds(thresholds);
      setNotification({ type: 'success', msg: 'Thresholds updated successfully.' });
      setTimeout(() => setNotification(null), 3000);
    } catch (err) {
      setNotification({ type: 'error', msg: 'Failed to update thresholds.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center animate-pulse text-gray-500">Loading settings...</div>;
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Adjust the heuristics and thresholds for the hybrid analyzer.
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
             <Settings2 className="w-5 h-5 text-primary-500" />
             <CardTitle>Decision Thresholds & Weights</CardTitle>
          </div>
          <CardDescription>Changes apply immediately to upcoming analysis requests.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">ML Confidence Threshold</label>
                <span className="text-sm text-gray-500">{thresholds.ml_confidence_threshold}</span>
              </div>
              <input 
                type="range" min="0" max="1" step="0.05" 
                value={thresholds.ml_confidence_threshold}
                onChange={(e) => handleChange('ml_confidence_threshold', parseFloat(e.target.value))}
                className="w-full accent-primary-600 focus:outline-none"
              />
              <p className="text-xs text-gray-400 mt-1">Minimum probability required to flag strictly via ML.</p>
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">OSINT Risk Threshold</label>
                <span className="text-sm text-gray-500">{thresholds.osint_risk_threshold}</span>
              </div>
              <input 
                type="range" min="0" max="1" step="0.05" 
                value={thresholds.osint_risk_threshold}
                onChange={(e) => handleChange('osint_risk_threshold', parseFloat(e.target.value))}
                className="w-full accent-primary-600 focus:outline-none"
              />
               <p className="text-xs text-gray-400 mt-1">Risk score limit to trigger OSINT warnings.</p>
            </div>

            <div className="pt-4 border-t border-gray-100 dark:border-gray-800">
               <h4 className="text-sm font-semibold mb-4 text-gray-900 dark:text-gray-100">Hybrid Ensemble Weights</h4>
               <div className="grid grid-cols-2 gap-6">
                 <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm text-gray-700 dark:text-gray-300">Machine Learning</label>
                      <span className="text-sm text-gray-500">{Math.round(thresholds.hybrid_weight_ml * 100)}%</span>
                    </div>
                    <input 
                      type="range" min="0" max="1" step="0.1" 
                      value={thresholds.hybrid_weight_ml}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value);
                        setThresholds((p: Thresholds) => ({ ...p, hybrid_weight_ml: val, hybrid_weight_osint: parseFloat((1 - val).toFixed(1)) }));
                      }}
                      className="w-full accent-blue-500 focus:outline-none"
                    />
                 </div>
                 <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm text-gray-700 dark:text-gray-300">OSINT Check</label>
                      <span className="text-sm text-gray-500">{Math.round(thresholds.hybrid_weight_osint * 100)}%</span>
                    </div>
                    <input 
                      type="range" min="0" max="1" step="0.1" 
                      value={thresholds.hybrid_weight_osint}
                      disabled
                      className="w-full accent-yellow-500 opacity-50 cursor-not-allowed"
                    />
                 </div>
               </div>
            </div>
          </div>

          {notification && (
            <div className={`p-3 rounded text-sm font-medium ${notification.type === 'success' ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'}`}>
              {notification.msg}
            </div>
          )}

          <div className="flex justify-end pt-4">
            <Button onClick={handleSave} isLoading={saving}>
              Save Configurations
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
