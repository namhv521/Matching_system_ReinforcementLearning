import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import type { TrainingCurvesResponse } from '../../types/api';

interface TrainingCurvesChartProps {
  curves: TrainingCurvesResponse;
}

export function TrainingCurvesChart({ curves }: TrainingCurvesChartProps) {
  const milestones = [500000, 1000000, 2000000];

  const chartData = milestones.map(m => {
    const ppoPoint = curves.ppo?.find(p => p.milestone === m);
    const a2cPoint = curves.a2c?.find(p => p.milestone === m);
    const dqnPoint = curves.dqn?.find(p => p.milestone === m);
    const qrdqnPoint = curves.qrdqn?.find(p => p.milestone === m);

    return {
      step: `${m / 1000000}M`,
      PPO: ppoPoint ? Number(ppoPoint.val_compatibility.toFixed(4)) : null,
      A2C: a2cPoint ? Number(a2cPoint.val_compatibility.toFixed(4)) : null,
      DQN: dqnPoint ? Number(dqnPoint.val_compatibility.toFixed(4)) : null,
      QRDQN: qrdqnPoint ? Number(qrdqnPoint.val_compatibility.toFixed(4)) : null,
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Đường cong Hội tụ Học Tăng cường Sâu (Convergence Curves)</CardTitle>
        <CardDescription>
          Theo dõi độ tương thích trên tập Validation qua 2.000.000 timesteps huấn luyện
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="step" tick={{ fontSize: 11 }} stroke="#64748b" />
              <YAxis tick={{ fontSize: 11 }} stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#cbd5e1',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="PPO"
                stroke="#4f46e5"
                strokeWidth={2.5}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="A2C"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="DQN"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="QRDQN"
                stroke="#ec4899"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
