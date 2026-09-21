import React from 'react';
import { BenchmarkChart } from './BenchmarkChart';
import { TrainingCurvesChart } from './TrainingCurvesChart';
import { ResearchFiguresGallery } from './ResearchFiguresGallery';
import { Skeleton } from '../../components/ui/Skeleton';
import { Alert } from '../../components/ui/Alert';
import { useBenchmarks, useTrainingCurves } from '../../hooks/useMatchingData';

export function BenchmarkAnalytics() {
  const { data: benchmarks, isLoading: isBenchLoading, isError: isBenchError } = useBenchmarks();
  const { data: curves, isLoading: isCurvesLoading, isError: isCurvesError } = useTrainingCurves();

  if (isBenchLoading || isCurvesLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 w-full rounded-xl" />
          <Skeleton className="h-80 w-full rounded-xl" />
        </div>
      </div>
    );
  }

  if (isBenchError || isCurvesError) {
    return (
      <Alert variant="error" title="Không thể tải dữ liệu phân tích thực nghiệm">
        <p>Vui lòng đảm bảo backend đang chạy và thư mục outputs chứa đầy đủ dữ liệu kết quả.</p>
      </Alert>
    );
  }

  return (
    <div className="space-y-8">
      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {benchmarks && <BenchmarkChart benchmarks={benchmarks} />}
        {curves && <TrainingCurvesChart curves={curves} />}
      </div>

      {/* Figures Gallery */}
      <ResearchFiguresGallery />
    </div>
  );
}
