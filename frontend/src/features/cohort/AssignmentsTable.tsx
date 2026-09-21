import React, { useState, useMemo } from 'react';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { AssignmentRow } from './AssignmentRow';
import type { CohortAssignment } from '../../types/api';

export function AssignmentsTable({ assignments }: { assignments: CohortAssignment[] }) {
  const [q, setQ] = useState('');
  const [adv, setAdv] = useState('ALL');
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const advisors = useMemo(() => {
    return Array.from(new Set(assignments.map(a => a.assigned_advisor_name))).sort();
  }, [assignments]);

  const filtered = useMemo(() => {
    const term = q.toLowerCase();
    return assignments.filter(item => {
      const matchSearch =
        !term ||
        item.student_name.toLowerCase().includes(term) ||
        item.student_id.toLowerCase().includes(term) ||
        item.thesis_title.toLowerCase().includes(term) ||
        item.assigned_advisor_name.toLowerCase().includes(term);
      const matchAdv = adv === 'ALL' || item.assigned_advisor_name === adv;
      return matchSearch && matchAdv;
    });
  }, [assignments, q, adv]);

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const paginated = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, page]);

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-72">
          <Input
            placeholder="Tìm theo SV, MSSV, đề tài..."
            value={q}
            onChange={e => { setQ(e.target.value); setPage(1); }}
            className="pl-9 text-xs"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
        </div>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={adv}
            onChange={e => { setAdv(e.target.value); setPage(1); }}
            className="h-10 text-xs rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-slate-700"
          >
            <option value="ALL">Tất cả GVHD ({advisors.length})</option>
            {advisors.map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
          <span className="text-xs text-slate-500 whitespace-nowrap">{filtered.length} kết quả</span>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-[11px] font-semibold uppercase text-slate-500 border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3 w-10 text-center">#</th>
                <th className="py-2.5 px-4 w-40">Sinh viên</th>
                <th className="py-2.5 px-4">Tên Đề tài KLTN</th>
                <th className="py-2.5 px-4 w-44">GVHD Phân bổ</th>
                <th className="py-2.5 px-3 text-right w-24">Tương thích</th>
                <th className="py-2.5 px-4 w-36">GV Lịch sử</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginated.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-500">
                    Không tìm thấy đề tài nào phù hợp với bộ lọc.
                  </td>
                </tr>
              ) : (
                paginated.map(item => <AssignmentRow key={item.step} item={item} />)
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-t border-slate-200">
          <span className="text-xs text-slate-500">Trang {page} / {totalPages}</span>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="h-7 w-7 p-0"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="h-7 w-7 p-0"
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
