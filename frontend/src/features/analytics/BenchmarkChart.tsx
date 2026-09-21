import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import type { BenchmarkItem } from '../../types/api';

interface BenchmarkChartProps {
  benchmarks: BenchmarkItem[];
}

export function BenchmarkChart({ benchmarks }: BenchmarkChartProps) {
  const chartData = benchmarks.map(item => ({
    name: item.algorithm,
    compatibility: Number((item.mean_compatibility * 100).toFixed(2)),
    fairnessScore: Number(((1 - item.gini_index) * 100).toFixed(2)),
    violations: item.constraint_violations,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Đối sánh Đa Tiêu chí giữa các Thuật toán (Benchmark)</CardTitle>
        <CardDescription>
          So sánh độ tương thích trung bình và mức tuân thủ ràng buộc trên tập validation hiện hành
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#64748b" />
              <YAxis tick={{ fontSize: 11 }} stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#cbd5e1',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar
                dataKey="compatibility"
                name="Tương thích TB (%)"
                fill="#4f46e5"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="fairnessScore"
                name="Chỉ số Công bằng (1-Gini) %"
                fill="#10b981"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
