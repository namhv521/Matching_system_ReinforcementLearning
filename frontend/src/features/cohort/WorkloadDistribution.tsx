import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import { Progress } from '../../components/ui/Progress';
import type { AdvisorWorkload } from '../../types/api';

interface WorkloadDistributionProps {
  workload: AdvisorWorkload[];
}

export function WorkloadDistribution({ workload }: WorkloadDistributionProps) {
  const sorted = [...workload].sort((a, b) => b.utilization_pct - a.utilization_pct);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Tải trọng Hướng dẫn & Sử dụng Chỉ tiêu (Quota Utilization)</CardTitle>
            <CardDescription>
              Kiểm tra tình trạng quá tải hoặc bất bình đẳng trong phân bổ giảng viên
            </CardDescription>
          </div>
          <span className="text-xs font-semibold text-slate-500">{workload.length} giảng viên</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {sorted.map(item => (
            <div
              key={item.advisor_name}
              className="p-3 rounded-lg border border-slate-100 bg-slate-50/50 space-y-1.5"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-900 truncate max-w-[160px]" title={item.advisor_name}>
                  {item.advisor_name}
                </span>
                <span className="text-slate-500 font-mono">
                  {item.assigned}/{item.capacity} đề tài
                </span>
              </div>
              <Progress value={item.assigned} max={item.capacity} />
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Còn lại: {item.remaining}</span>
                <span
                  className={`font-semibold ${
                    item.utilization_pct >= 100
                      ? 'text-rose-600'
                      : item.utilization_pct >= 75
                      ? 'text-amber-600'
                      : 'text-emerald-600'
                  }`}
                >
                  {item.utilization_pct}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
