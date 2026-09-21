import React from 'react';
import {
  LayoutDashboard,
  GitMerge,
  UserCheck,
  Users,
  LineChart,
} from 'lucide-react';
import { cn } from '../../lib/utils';

export type ActiveTab = 'overview' | 'cohort' | 'recommend' | 'advisors' | 'analytics';

interface NavigationProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
}

export function Navigation({ activeTab, onTabChange }: NavigationProps) {
  const tabs = [
    {
      id: 'overview' as ActiveTab,
      label: 'Tổng quan Hệ thống',
      icon: LayoutDashboard,
      badge: 'KPIs',
    },
    {
      id: 'cohort' as ActiveTab,
      label: 'Mô phỏng Phân bổ Đợt',
      icon: GitMerge,
      badge: 'Chính',
    },
    {
      id: 'recommend' as ActiveTab,
      label: 'Gợi ý GVHD Đề tài',
      icon: UserCheck,
      badge: 'Interactive',
    },
    {
      id: 'advisors' as ActiveTab,
      label: 'Danh bạ Giảng viên',
      icon: Users,
      badge: null,
    },
    {
      id: 'analytics' as ActiveTab,
      label: 'Đo lường & Sơ đồ KLTN',
      icon: LineChart,
      badge: 'RL & Sơ đồ',
    },
  ];

  return (
    <nav className="w-full bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-1 sm:space-x-4 overflow-x-auto py-2.5 no-scrollbar">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => onTabChange(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap transition-all cursor-pointer',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 shadow-sm font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                )}
              >
                <Icon className={cn('w-4 h-4', isActive ? 'text-indigo-600' : 'text-slate-400')} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    className={cn(
                      'text-[10px] px-1.5 py-0.2 rounded font-semibold',
                      isActive ? 'bg-indigo-200/80 text-indigo-900' : 'bg-slate-100 text-slate-500'
                    )}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
