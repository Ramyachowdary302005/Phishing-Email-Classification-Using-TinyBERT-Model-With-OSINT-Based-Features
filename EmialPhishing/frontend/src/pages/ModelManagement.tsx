import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Progress } from '../components/common/Progress';
import { api } from '../services/api';
import { TrainModelResponse } from '../types';
import { Network, Cpu, Settings, Activity } from 'lucide-react';

export function ModelManagement() {
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<TrainModelResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrainModel = async () => {
    setLoading(true);
    setError(null);
    try {
      // POST /train-model
      const res = await api.trainModel();
      setMetrics(res);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to trigger model training.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Management</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Perform TinyBERT re-training, analyze metrics, and manage model states.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Actions Card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Training Control</CardTitle>
            <CardDescription>Initiate a new model training job on the backend.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
               <div className="flex items-center space-x-3 mb-2">
                 <Network className="text-primary-500" />
                 <span className="font-medium text-sm">Active Model: TinyBERT_v2</span>
               </div>
               <p className="text-xs text-gray-500">Params: 14.5M | Classes: 2</p>
            </div>
            
            {error && <div className="text-sm text-red-500 bg-red-50 dark:bg-red-900/10 p-2 rounded">{error}</div>}

            <Button 
              className="w-full" 
              onClick={handleTrainModel} 
              isLoading={loading}
              disabled={loading}
            >
              {loading ? 'Training in Progress...' : 'Start Model Training'}
            </Button>
            <p className="text-xs text-gray-400 text-center">Note: Training depends on backend availability and GPU resources.</p>
          </CardContent>
        </Card>

        {/* Metrics View */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Evaluation Metrics</CardTitle>
            <CardDescription>Results from the latest training job.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
               <div className="flex flex-col items-center justify-center p-12 space-y-4">
                <Cpu className="w-10 h-10 text-primary-500 animate-pulse" />
                <div className="text-lg font-semibold animate-pulse">Fine-tuning TinyBERT...</div>
                <Progress value={45} className="w-64 mt-4" />
                <p className="text-xs text-gray-500">Epoch 2/5</p>
              </div>
            ) : metrics ? (
              <div className="grid grid-cols-2 gap-4">
                {/* Accuracy */}
                <div className="p-4 rounded-lg bg-white dark:bg-dark-bg border border-gray-100 dark:border-gray-800">
                  <div className="text-sm text-gray-500 font-medium mb-1">Accuracy</div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                    {(metrics.metrics.accuracy * 100).toFixed(2)}%
                  </div>
                  <Progress value={metrics.metrics.accuracy * 100} className="h-2 mt-2" indicatorClassName="bg-green-500"/>
                </div>
                {/* F1 Score */}
                <div className="p-4 rounded-lg bg-white dark:bg-dark-bg border border-gray-100 dark:border-gray-800">
                  <div className="text-sm text-gray-500 font-medium mb-1">F1 Score</div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                    {(metrics.metrics.f1_score * 100).toFixed(2)}
                  </div>
                  <Progress value={metrics.metrics.f1_score * 100} className="h-2 mt-2" indicatorClassName="bg-blue-500"/>
                </div>
                {/* Precision */}
                <div className="p-4 rounded-lg bg-white dark:bg-dark-bg border border-gray-100 dark:border-gray-800">
                  <div className="text-sm text-gray-500 font-medium mb-1">Precision</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {(metrics.metrics.precision * 100).toFixed(2)}%
                  </div>
                </div>
                {/* Recall */}
                <div className="p-4 rounded-lg bg-white dark:bg-dark-bg border border-gray-100 dark:border-gray-800">
                  <div className="text-sm text-gray-500 font-medium mb-1">Recall</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {(metrics.metrics.recall * 100).toFixed(2)}%
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-12 text-gray-400">
                <Activity className="w-12 h-12 mb-4 opacity-30" />
                <p>Run training to display latest evaluation metrics.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
