import React from 'react';
import {
  FileText,
  Users,
  Award,
  Zap,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';
import { StatCard } from './StatCard';
import { SplitBreakdown } from './SplitBreakdown';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Skeleton } from '../../components/ui/Skeleton';
import { Alert } from '../../components/ui/Alert';
import { useOverview } from '../../hooks/useMatchingData';

interface OverviewDashboardProps {
  onNavigate: (tab: 'cohort' | 'recommend' | 'advisors' | 'analytics') => void;
}

export function OverviewDashboard({ onNavigate }: OverviewDashboardProps) {
  const { data: overview, isLoading, isError, error, refetch } = useOverview();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="p-5">
              <Skeleton className="h-4 w-24 mb-3" />
              <Skeleton className="h-8 w-16 mb-2" />
              <Skeleton className="h-3 w-32" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !overview) {
    return (
      <Alert variant="error" title="Không thể tải tổng quan hệ thống">
        <p>{error instanceof Error ? error.message : 'Lỗi kết nối API backend.'}</p>
        <Button variant="outline" size="sm" onClick={() => refetch()} className="mt-3">
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Thử lại
        </Button>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tổng Khóa luận"
          value={overview.total_theses}
          subtitle="Dữ liệu thực nghiệm KLTN"
          icon={FileText}
          iconBg="bg-blue-50"
          iconColor="text-blue-600"
          trend={`${overview.total_theses} bản ghi curated`}
        />
        <StatCard
          title="Hội đồng Giảng viên"
          value={overview.total_advisors}
          subtitle="Giáo sư, PGS, TS, ThS"
          icon={Users}
          iconBg="bg-emerald-50"
          iconColor="text-emerald-600"
          trend="Đủ chỉ tiêu hướng dẫn"
        />
        <StatCard
          title="Thuật toán Tiêu chuẩn"
          value={overview.promoted_engine === 'exact' ? 'Hungarian Exact' : overview.promoted_engine}
          subtitle="Toàn cục (Global Optimal)"
          icon={Award}
          iconBg="bg-indigo-50"
          iconColor="text-indigo-600"
          trend="0 vi phạm chỉ tiêu"
        />
        <StatCard
          title="Top RL Policy"
          value={overview.top_rl_engine === 'ppo_maskable' ? 'Maskable PPO' : overview.top_rl_engine}
          subtitle="Học tăng cường có Masking"
          icon={Zap}
          iconBg="bg-amber-50"
          iconColor="text-amber-600"
          trend={`Điểm: ${overview.top_rl_compatibility.toFixed(4)}`}
        />
      </div>

      {/* Production Promotion Banner */}
      <div className="rounded-2xl border border-indigo-200/80 bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 text-white p-6 sm:p-7 shadow-md">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center gap-2">
              <Badge variant="purple" className="bg-indigo-500/30 text-indigo-100 border-indigo-400/40">
                <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                Kiến trúc Dual-Engine
              </Badge>
            </div>
            <h3 className="text-xl font-bold tracking-tight text-white">
              Phân bổ Tối ưu Toàn cục & Mô phỏng Tuần tự bằng Deep RL
            </h3>
            <p className="text-xs sm:text-sm text-indigo-100/90 leading-relaxed">
              {overview.promoted_reason}
              <br />
              Mô hình <strong className="text-amber-300">Maskable PPO</strong> được ứng dụng khi sinh viên đăng ký theo dòng thời gian thực, đảm bảo không vi phạm quota nhờ action masking.
            </p>
          </div>
          <div className="flex flex-wrap gap-2.5 shrink-0">
            <Button
              variant="primary"
              onClick={() => onNavigate('cohort')}
              className="bg-white text-indigo-900 hover:bg-indigo-50 font-semibold"
            >
              Chạy Phân bổ Đợt <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
            <Button
              variant="outline"
              onClick={() => onNavigate('recommend')}
              className="border-indigo-300 text-white bg-indigo-800/40 hover:bg-indigo-700/60"
            >
              Gợi ý Nhanh Đề tài
            </Button>
          </div>
        </div>
      </div>

      {/* Grid: Dataset Splits & Quick Actions */}
      <SplitBreakdown splits={overview.splits} onNavigate={onNavigate} />
    </div>
  );
}
