import React from 'react';
import { RecommendationForm, type RecommendFormData } from './RecommendationForm';
import { AdvisorCard } from './AdvisorCard';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { useRecommendMutation } from '../../hooks/useMatchingData';

export function AdvisorRecommender() {
  const recommendMutation = useRecommendMutation();

  const handleFormSubmit = (data: RecommendFormData) => {
    recommendMutation.mutate({
      title: data.title,
      field: data.field,
      tech_stack: data.tech_stack,
      top_k: data.top_k,
    });
  };

  const response = recommendMutation.data;
  const isLoading = recommendMutation.isPending;

  return (
    <div className="space-y-6">
      {/* Search Input Form */}
      <RecommendationForm onSubmit={handleFormSubmit} isLoading={isLoading} />

      {/* Error Display */}
      {recommendMutation.isError && (
        <Alert variant="error" title="Gợi ý GVHD thất bại">
          <p>{recommendMutation.error instanceof Error ? recommendMutation.error.message : 'Lỗi kết nối'}</p>
        </Alert>
      )}

      {/* Results Header and Cards */}
      {response && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-4 rounded-xl bg-white border border-slate-200">
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-bold text-slate-900 text-base">Kết quả Phù hợp Nhất</h4>
                <Badge variant="purple">{response.recommendations.length} Giảng viên</Badge>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Đề tài: &ldquo;<span className="font-medium text-slate-800">{response.query.title}</span>&rdquo;
              </p>
            </div>
            {response.query.tech_stack && (
              <span className="text-xs text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100 font-mono">
                {response.query.tech_stack}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {response.recommendations.map(advisor => (
              <AdvisorCard key={advisor.advisor_id} advisor={advisor} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
