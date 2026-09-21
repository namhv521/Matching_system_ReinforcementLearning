import React from 'react';
import { Card, CardContent } from '../../components/ui/Card';
import { cn } from '../../lib/utils';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  iconBg?: string;
  iconColor?: string;
  trend?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconBg = 'bg-indigo-50',
  iconColor = 'text-indigo-600',
  trend,
}: StatCardProps) {
  return (
    <Card className="hover:border-slate-300 transition-all hover:shadow">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
            <h4 className="text-2xl font-bold text-slate-900 mt-1.5">{value}</h4>
            {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
            {trend && <p className="text-xs font-medium text-emerald-600 mt-1">{trend}</p>}
          </div>
          <div className={cn('p-3 rounded-xl flex items-center justify-center', iconBg)}>
            <Icon className={cn('w-6 h-6', iconColor)} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
