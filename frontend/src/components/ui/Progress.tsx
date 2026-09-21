import React from 'react';
import { cn } from '../../lib/utils';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number; // 0 to 100
  max?: number;
  showLabel?: boolean;
}

export function Progress({ value, max = 100, showLabel = false, className, ...props }: ProgressProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  let barColor = 'bg-indigo-600';
  if (percentage >= 100) {
    barColor = 'bg-rose-500';
  } else if (percentage >= 80) {
    barColor = 'bg-amber-500';
  } else {
    barColor = 'bg-emerald-500';
  }

  return (
    <div className={cn('w-full space-y-1', className)} {...props}>
      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className={cn('h-full transition-all duration-300 ease-in-out rounded-full', barColor)}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between text-xs text-slate-500 font-medium">
          <span>{percentage.toFixed(0)}%</span>
          <span>
            {value} / {max}
          </span>
        </div>
      )}
    </div>
  );
}
