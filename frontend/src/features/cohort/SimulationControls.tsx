import React from 'react';
import { Play } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import type { DatasetSplit, AllocationAlgorithm } from '../../types/api';

interface SimulationControlsProps {
  split: DatasetSplit;
  algorithm: AllocationAlgorithm;
  isLoading: boolean;
  onSplitChange: (s: DatasetSplit) => void;
  onAlgorithmChange: (a: AllocationAlgorithm) => void;
  onRun: () => void;
}

export function SimulationControls({
  split,
  algorithm,
  isLoading,
  onSplitChange,
  onAlgorithmChange,
  onRun,
}: SimulationControlsProps) {
  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <CardTitle>Mô phỏng Phân bổ Đợt Khóa luận Hàng loạt</CardTitle>
            <CardDescription>
              Thử nghiệm và đối sánh các thuật toán phân bổ trên các tập dữ liệu thực tế
            </CardDescription>
          </div>
          <Button variant="primary" onClick={onRun} isLoading={isLoading} className="gap-1.5">
            <Play className="w-4 h-4 fill-white" />
            Chạy Phân bổ
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
              Tập dữ liệu Khóa luận
            </label>
            <select
              value={split}
              onChange={e => onSplitChange(e.target.value as DatasetSplit)}
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="validation">Validation Split (holdout 2025)</option>
              <option value="test">Test Split (holdout 2025, chỉ đánh giá cuối)</option>
              <option value="train">Train Split (trước 2025 + 75% năm 2025)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
              Thuật toán Phân bổ
            </label>
            <select
              value={algorithm}
              onChange={e => onAlgorithmChange(e.target.value as AllocationAlgorithm)}
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="exact">Hungarian Exact (Tối ưu toàn cục)</option>
              <option value="ppo_maskable">Maskable PPO (RL Policy có Action Masking)</option>
              <option value="gale_shapley">Gale-Shapley (Deferred Acceptance)</option>
              <option value="greedy">Greedy Heuristic (Tham lam cục bộ)</option>
              <option value="random">Random Baseline (Ngẫu nhiên đối chứng)</option>
            </select>
          </div>

          <div className="flex items-end text-xs text-slate-500 leading-relaxed">
            {algorithm === 'exact' && 'Hungarian tìm cực đại tổng điểm tương thích toàn cục trong O(N³).'}
            {algorithm === 'ppo_maskable' && 'Mô hình RL duyệt tuần tự, action mask loại trừ giảng viên hết chỉ tiêu.'}
            {algorithm === 'gale_shapley' && 'Thuật toán hai phía ngăn ngừa blocking pairs.'}
            {algorithm === 'greedy' && 'Gán đề tài cho GVHD còn chỉ tiêu có điểm cao nhất.'}
            {algorithm === 'random' && 'Phân bổ ngẫu nhiên kiểm tra giới hạn dưới của hệ thống.'}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
