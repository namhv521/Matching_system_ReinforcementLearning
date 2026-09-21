import React, { useState, useMemo } from 'react';
import { Search, Users, RefreshCw } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Alert } from '../../components/ui/Alert';
import { AdvisorDirectoryCard } from './AdvisorDirectoryCard';
import { useAdvisors } from '../../hooks/useMatchingData';

export function AdvisorsDirectory() {
  const { data: advisors, isLoading, isError, error, refetch } = useAdvisors();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedField, setSelectedField] = useState('ALL');

  const fields = useMemo(() => {
    if (!advisors) return [];
    return Array.from(new Set(advisors.map(a => a.primary_field).filter(Boolean))).sort();
  }, [advisors]);

  const filtered = useMemo(() => {
    if (!advisors) return [];
    const q = searchTerm.toLowerCase();
    return advisors.filter(item => {
      const matchSearch =
        !q ||
        item.advisor_name.toLowerCase().includes(q) ||
        (item.academic_title && item.academic_title.toLowerCase().includes(q)) ||
        item.primary_field.toLowerCase().includes(q) ||
        item.skills.some(s => s.toLowerCase().includes(q));

      const matchField = selectedField === 'ALL' || item.primary_field === selectedField;
      return matchSearch && matchField;
    });
  }, [advisors, searchTerm, selectedField]);

  const totalCapacity = useMemo(() => {
    if (!advisors) return 0;
    return advisors.reduce((acc, a) => acc + a.capacity, 0);
  }, [advisors]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-12 w-full" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Card key={i} className="p-5">
              <Skeleton className="h-5 w-32 mb-2" />
              <Skeleton className="h-16 w-full" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !advisors) {
    return (
      <Alert variant="error" title="Không thể tải danh bạ giảng viên">
        <p>{error instanceof Error ? error.message : 'Lỗi kết nối API'}</p>
        <Button variant="outline" size="sm" onClick={() => refetch()} className="mt-3">
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Thử lại
        </Button>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-600" />
            <h3 className="font-bold text-slate-900 text-lg">Hội đồng Giảng viên Hướng dẫn</h3>
            <Badge variant="purple">{advisors.length} Giảng viên</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Tổng chỉ tiêu hướng dẫn: <strong className="text-slate-800">{totalCapacity} đề tài</strong> KLTN
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <div className="relative w-full sm:w-64">
            <Input
              placeholder="Tìm theo tên, kỹ năng..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9 text-xs"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          </div>

          <select
            value={selectedField}
            onChange={e => setSelectedField(e.target.value)}
            className="h-10 text-xs rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-slate-700"
          >
            <option value="ALL">Tất cả lĩnh vực ({fields.length})</option>
            {fields.map(f => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(advisor => (
          <AdvisorDirectoryCard key={advisor.advisor_id} advisor={advisor} />
        ))}
      </div>
    </div>
  );
}
