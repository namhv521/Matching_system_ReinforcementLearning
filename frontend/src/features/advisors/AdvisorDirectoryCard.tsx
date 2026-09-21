import React from 'react';
import { Mail, BookOpen, GraduationCap } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import type { Advisor } from '../../types/api';

export function AdvisorDirectoryCard({ advisor }: { advisor: Advisor }) {
  return (
    <Card className="hover:border-indigo-300 hover:shadow-xs transition-all">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-700 shrink-0">
              <GraduationCap className="w-4 h-4 text-indigo-600" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-sm">{advisor.advisor_name}</h4>
              <p className="text-[11px] text-slate-500">{advisor.academic_title || 'Giảng viên'}</p>
            </div>
          </div>
          <Badge variant="purple" className="text-[10px] py-0">
            {advisor.capacity} chỉ tiêu
          </Badge>
        </div>

        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-1 text-slate-600">
            <span className="font-medium text-slate-700">Lĩnh vực:</span>
            <span className="text-slate-900 font-semibold">{advisor.primary_field}</span>
          </div>
          {advisor.publication_count > 0 && (
            <div className="flex items-center gap-1 text-slate-500 text-[11px]">
              <BookOpen className="w-3 h-3" />
              <span>{advisor.publication_count} công trình nghiên cứu</span>
            </div>
          )}
        </div>

        {advisor.skills && advisor.skills.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-0.5">
            {advisor.skills.slice(0, 5).map((skill, sIdx) => (
              <span key={sIdx} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                {skill}
              </span>
            ))}
          </div>
        )}

        {advisor.email && (
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-400 font-mono text-[11px] truncate max-w-[150px]">
              {advisor.email}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.open(`mailto:${advisor.email}`, '_blank')}
              className="h-6 text-xs px-2 gap-1 text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50"
            >
              <Mail className="w-3 h-3" /> Gửi mail
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
