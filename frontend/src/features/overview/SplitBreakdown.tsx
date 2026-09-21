import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { ArrowRight, BarChart3 } from 'lucide-react';

interface SplitBreakdownProps {
  splits: { train: number; validation: number; test: number };
  onNavigate: (tab: 'cohort' | 'recommend' | 'advisors' | 'analytics') => void;
}

export function SplitBreakdown({ splits, onNavigate }: SplitBreakdownProps) {
  const totalSplits = splits.train + splits.validation + splits.test;
  const trainPct = Math.round((splits.train / totalSplits) * 100);
  const valPct = Math.round((splits.validation / totalSplits) * 100);
  const testPct = Math.round((splits.test / totalSplits) * 100);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Phân chia Tập dữ liệu Khóa luận (Temporal Split)</CardTitle>
              <CardDescription>Tách theo nhóm sinh viên và thời gian để giảm nguy cơ rò rỉ dữ liệu</CardDescription>
            </div>
            <Badge variant="outline">{totalSplits} đề tài</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex">
            <div style={{ width: `${trainPct}%` }} className="bg-indigo-600 h-full" title={`Train: ${trainPct}%`} />
            <div style={{ width: `${valPct}%` }} className="bg-blue-500 h-full" title={`Validation: ${valPct}%`} />
            <div style={{ width: `${testPct}%` }} className="bg-emerald-500 h-full" title={`Test: ${testPct}%`} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">Train Split</span>
              <p className="text-lg font-bold text-slate-900 mt-1">{splits.train}</p>
              <p className="text-[10px] text-slate-500">Trước 2025 + 75% năm 2025 ({trainPct}%)</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">Validation Split</span>
              <p className="text-lg font-bold text-slate-900 mt-1">{splits.validation}</p>
              <p className="text-[10px] text-slate-500">Holdout năm 2025 ({valPct}%)</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">Test Split</span>
              <p className="text-lg font-bold text-slate-900 mt-1">{splits.test}</p>
              <p className="text-[10px] text-slate-500">Khóa 2025 ({testPct}%)</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quy trình Nghiệp vụ</CardTitle>
          <CardDescription>Các phân hệ chính hỗ trợ hội đồng</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2.5">
          <button
            type="button"
            onClick={() => onNavigate('cohort')}
            className="w-full text-left p-3 rounded-xl border border-slate-200/80 hover:border-indigo-400 hover:bg-indigo-50/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-900 group-hover:text-indigo-700">
                Mô phỏng đợt bảo vệ KLTN
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600" />
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">Phân bổ đồng thời với Hungarian hoặc PPO</p>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('recommend')}
            className="w-full text-left p-3 rounded-xl border border-slate-200/80 hover:border-indigo-400 hover:bg-indigo-50/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-900 group-hover:text-indigo-700">
                Gợi ý GVHD cho đề tài mới
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600" />
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">Khớp semantic TF-IDF & Cosine Similarity</p>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('analytics')}
            className="w-full text-left p-3 rounded-xl border border-slate-200/80 hover:border-indigo-400 hover:bg-indigo-50/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-900 group-hover:text-indigo-700">
                Đo lường & Sơ đồ KLTN
              </span>
              <BarChart3 className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600" />
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">So sánh benchmark và kiểm tra hội tụ RL 2M steps</p>
          </button>
        </CardContent>
      </Card>
    </div>
  );
}
