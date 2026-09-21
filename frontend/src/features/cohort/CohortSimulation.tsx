import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Alert } from '../../components/ui/Alert';
import { Skeleton } from '../../components/ui/Skeleton';
import { SimulationControls } from './SimulationControls';
import { AllocationMetrics } from './AllocationMetrics';
import { AssignmentsTable } from './AssignmentsTable';
import { WorkloadDistribution } from './WorkloadDistribution';
import { useCohortMatchMutation } from '../../hooks/useMatchingData';
import type { DatasetSplit, AllocationAlgorithm } from '../../types/api';

export function CohortSimulation() {
  const [split, setSplit] = useState<DatasetSplit>('validation');
  const [algorithm, setAlgorithm] = useState<AllocationAlgorithm>('exact');
  const [activeSubTab, setActiveSubTab] = useState<'assignments' | 'workload'>('assignments');

  const matchMutation = useCohortMatchMutation();

  const handleRun = () => {
    matchMutation.mutate({ split, algorithm });
  };

  useEffect(() => {
    matchMutation.mutate({ split: 'validation', algorithm: 'exact' });
  }, []);

  const result = matchMutation.data;
  const isLoading = matchMutation.isPending;

  return (
    <div className="space-y-6">
      <SimulationControls
        split={split}
        algorithm={algorithm}
        isLoading={isLoading}
        onSplitChange={setSplit}
        onAlgorithmChange={setAlgorithm}
        onRun={handleRun}
      />

      {matchMutation.isError && (
        <Alert variant="error" title="Mô phỏng phân bổ thất bại">
          <p>{matchMutation.error instanceof Error ? matchMutation.error.message : 'Đã có lỗi xảy ra.'}</p>
        </Alert>
      )}

      {isLoading && !result && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            {[1, 2, 3, 4, 5].map(i => (
              <Card key={i} className="p-4">
                <Skeleton className="h-4 w-20 mb-2" />
                <Skeleton className="h-6 w-16" />
              </Card>
            ))}
          </div>
          <Card className="p-6">
            <Skeleton className="h-8 w-48 mb-4" />
            <Skeleton className="h-48 w-full" />
          </Card>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <AllocationMetrics metrics={result.metrics} cohortSize={result.cohort_size} />

          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setActiveSubTab('assignments')}
              className={`py-2.5 px-4 text-xs sm:text-sm font-semibold border-b-2 transition-colors cursor-pointer ${
                activeSubTab === 'assignments'
                  ? 'border-indigo-600 text-indigo-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Bảng Phân bổ Chi tiết ({result.assignments.length})
            </button>
            <button
              onClick={() => setActiveSubTab('workload')}
              className={`py-2.5 px-4 text-xs sm:text-sm font-semibold border-b-2 transition-colors cursor-pointer ${
                activeSubTab === 'workload'
                  ? 'border-indigo-600 text-indigo-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Phân bổ Tải trọng GVHD ({result.workload_distribution.length})
            </button>
          </div>

          {activeSubTab === 'assignments' ? (
            <AssignmentsTable assignments={result.assignments} />
          ) : (
            <WorkloadDistribution workload={result.workload_distribution} />
          )}
        </div>
      )}
    </div>
  );
}
