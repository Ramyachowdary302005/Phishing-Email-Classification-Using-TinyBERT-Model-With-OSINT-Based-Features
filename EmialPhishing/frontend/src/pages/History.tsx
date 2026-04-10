import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { useHistory } from '../context/HistoryContext';
import { Search, Trash2 } from 'lucide-react';

export function History() {
  const { history, clearHistory } = useHistory();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredHistory = history.filter(item => 
    item.request.headers.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.response.final_decision.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.id.includes(searchTerm)
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Scan History</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Review past analysis records stored locally.
          </p>
        </div>
        {history.length > 0 && (
          <Button
            variant="danger"
            onClick={() => {
              if (window.confirm('Are you sure you want to clear all history?')) clearHistory();
            }}
            className="mt-4 md:mt-0"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear History
          </Button>
        )}
      </div>

      <Card>
        <CardHeader className="pb-4 border-b border-gray-100 dark:border-gray-800">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input 
              placeholder="Search by sender email, decision, or ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {filteredHistory.length === 0 ? (
             <div className="p-12 text-center text-gray-500">
               {searchTerm ? 'No results found.' : 'No scanning history available.'}
             </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 uppercase bg-gray-50 dark:bg-dark-card border-b dark:border-dark-border">
                  <tr>
                    <th className="px-6 py-4 font-medium">Date</th>
                    <th className="px-6 py-4 font-medium">Sender Email</th>
                    <th className="px-6 py-4 font-medium">Verdict</th>
                    <th className="px-6 py-4 font-medium">Confidence</th>
                    <th className="px-6 py-4 font-medium">Method</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((item) => (
                    <tr key={item.id} className="bg-white dark:bg-dark-card border-b dark:border-dark-border hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                        {new Date(item.date).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">
                        {item.request.headers.from}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={item.response.final_decision === 'Phishing' ? 'danger' : 'success'}>
                          {item.response.final_decision}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 font-bold">
                         {(item.response.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4">
                         {item.response.stage}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
