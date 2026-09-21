import React from 'react';
import { Card, CardContent } from '../../components/ui/Card';
import { Target, AlertTriangle, Scale, Clock, CheckCircle2 } from 'lucide-react';
import type { CohortMatchMetrics } from '../../types/api';

interface AllocationMetricsProps {
  metrics: CohortMatchMetrics;
  cohortSize: number;
}

export function AllocationMetrics({ metrics, cohortSize }: AllocationMetricsProps) {
  const isZeroViolations = metrics.constraint_violations === 0;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
      <Card className="border-slate-200 shadow-none bg-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Độ tương thích TB</span>
            <Target className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {metrics.mean_compatibility.toFixed(4)}
          </p>
          <span className="text-[11px] text-slate-400">Mean Compatibility</span>
        </CardContent>
      </Card>

      <Card className="border-slate-200 shadow-none bg-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Vi phạm Chỉ tiêu</span>
            {isZeroViolations ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-600" />
            )}
          </div>
          <p
            className={`text-xl font-bold mt-1 ${
              isZeroViolations ? 'text-emerald-700' : 'text-rose-600'
            }`}
          >
            {metrics.constraint_violations}
          </p>
          <span className="text-[11px] text-slate-400">Hard Quota Violations</span>
        </CardContent>
      </Card>

      <Card className="border-slate-200 shadow-none bg-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Hệ số Bất bình đẳng</span>
            <Scale className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {metrics.gini_index.toFixed(3)}
          </p>
          <span className="text-[11px] text-slate-400">Gini Load Index</span>
        </CardContent>
      </Card>

      <Card className="border-slate-200 shadow-none bg-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Thời gian Thực thi</span>
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {metrics.execution_time_ms} ms
          </p>
          <span className="text-[11px] text-slate-400">{cohortSize} sinh viên</span>
        </CardContent>
      </Card>

      <Card className="col-span-2 lg:col-span-1 border-slate-200 shadow-none bg-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Trùng Lịch sử</span>
            <span className="text-xs font-semibold text-slate-400">Historical</span>
          </div>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {metrics.accuracy_vs_historical
              ? `${(metrics.accuracy_vs_historical * 100).toFixed(1)}%`
              : 'N/A'}
          </p>
          <span className="text-[11px] text-slate-400">Khớp GVHD thực tế</span>
        </CardContent>
      </Card>
    </div>
  );
}
