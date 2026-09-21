import React from 'react';
import { Mail, GraduationCap, Award, BookOpen } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import type { AdvisorRecommendation } from '../../types/api';

interface AdvisorCardProps {
  advisor: AdvisorRecommendation;
}

export function AdvisorCard({ advisor }: AdvisorCardProps) {
  const scorePercent = (advisor.compatibility_score * 100).toFixed(1);

  const getRankBadgeVariant = (rank: number) => {
    if (rank === 1) return 'success';
    if (rank === 2) return 'purple';
    if (rank === 3) return 'warning';
    return 'default';
  };

  return (
    <Card className="hover:border-indigo-300 hover:shadow-md transition-all">
      <CardContent className="p-5 space-y-4">
        {/* Header: Rank + Name + Title */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700 font-bold">
              <GraduationCap className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-bold text-slate-900 text-base">{advisor.advisor_name}</h4>
                <Badge variant={getRankBadgeVariant(advisor.rank)} className="text-[10px] py-0 px-2 font-bold">
                  Top #{advisor.rank}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {advisor.academic_title ? `${advisor.academic_title} • ` : ''}
                {advisor.primary_field}
              </p>
            </div>
          </div>
        </div>

        {/* Compatibility Score Bar */}
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-700 flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-indigo-600" /> Điểm Tương thích Semantic:
            </span>
            <span className="font-bold font-mono text-indigo-700 text-sm">
              {advisor.compatibility_score.toFixed(4)} ({scorePercent}%)
            </span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-indigo-700 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, advisor.compatibility_score * 100 * 2.5)}%` }}
            />
          </div>
        </div>

        {/* Advisor Details */}
        <div className="flex items-center justify-between text-xs text-slate-600">
          <span className="flex items-center gap-1">
            <BookOpen className="w-3.5 h-3.5 text-slate-400" /> Chỉ tiêu hướng dẫn:
          </span>
          <span className="font-semibold text-slate-800">{advisor.capacity} đề tài</span>
        </div>

        {/* Skills Tags */}
        {advisor.skills && advisor.skills.length > 0 && (
          <div className="space-y-1">
            <span className="text-[11px] font-semibold text-slate-400">Từ khóa chuyên môn:</span>
            <div className="flex flex-wrap gap-1.5 pt-0.5">
              {advisor.skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-medium border border-indigo-100"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        {advisor.email && (
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono truncate max-w-[200px]">
              {advisor.email}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(`mailto:${advisor.email}`, '_blank')}
              className="h-7 text-xs gap-1.5"
            >
              <Mail className="w-3.5 h-3.5 text-slate-500" />
              Liên hệ
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
