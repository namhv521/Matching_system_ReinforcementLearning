import React from 'react';
import { Cpu, CheckCircle2, AlertCircle } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { useOverview } from '../../hooks/useMatchingData';

export function Header() {
  const { data: overview, isError, isLoading } = useOverview();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-800 text-white shadow-md shadow-indigo-200 font-bold text-lg">
              🎓
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight leading-tight">
                  KLTN Matching Decision Support
                </h1>
                <Badge variant="purple" className="hidden sm:inline-flex text-[11px] font-semibold py-0">
                  Dual-Engine
                </Badge>
              </div>
              <p className="text-xs text-slate-500 hidden md:block">
                Hệ thống Phân bổ Khóa luận Tốt nghiệp Tối ưu: Hungarian Exact & Maskable PPO Deep RL
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {isLoading ? (
              <div className="h-7 w-28 bg-slate-100 rounded-full animate-pulse" />
            ) : isError ? (
              <Badge variant="danger" className="text-xs py-1">
                <AlertCircle className="w-3.5 h-3.5" />
                Mất kết nối API
              </Badge>
            ) : (
              <div className="flex items-center gap-2">
                <div className="hidden lg:flex items-center gap-2 text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
                  <Cpu className="w-3.5 h-3.5 text-indigo-600" />
                  <span className="text-slate-600 font-medium">Engine chuẩn:</span>
                  <span className="font-semibold text-indigo-700 capitalize">
                    {overview?.promoted_engine || 'Exact'}
                  </span>
                </div>
                <Badge variant="success" className="text-xs py-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  API Sẵn sàng
                </Badge>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
