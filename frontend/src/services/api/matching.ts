/**
 * Matching Decision Support Service API calls
 */
import { apiClient } from './client';
import type {
  OverviewResponse,
  BenchmarkItem,
  TrainingCurvesResponse,
  Advisor,
  Thesis,
  MatchCohortRequest,
  CohortMatchResponse,
  RecommendRequest,
  RecommendResponse,
  FigureItem,
  DatasetSplit,
} from '../../types/api';

export const matchingApi = {
  getOverview: async (): Promise<OverviewResponse> => {
    return apiClient.get<OverviewResponse>('/api/overview');
  },

  getBenchmarks: async (): Promise<BenchmarkItem[]> => {
    return apiClient.get<BenchmarkItem[]>('/api/benchmarks');
  },

  getTrainingCurves: async (): Promise<TrainingCurvesResponse> => {
    return apiClient.get<TrainingCurvesResponse>('/api/training-curves');
  },

  getAdvisors: async (): Promise<Advisor[]> => {
    return apiClient.get<Advisor[]>('/api/advisors');
  },

  getTheses: async (split: DatasetSplit = 'validation', limit: number = 50): Promise<Thesis[]> => {
    return apiClient.get<Thesis[]>(`/api/theses?split=${encodeURIComponent(split)}&limit=${limit}`);
  },

  matchCohort: async (payload: MatchCohortRequest): Promise<CohortMatchResponse> => {
    return apiClient.post<CohortMatchResponse>('/api/match/cohort', payload);
  },

  recommendAdvisor: async (payload: RecommendRequest): Promise<RecommendResponse> => {
    return apiClient.post<RecommendResponse>('/api/match/recommend', payload);
  },

  getFigures: async (): Promise<FigureItem[]> => {
    return apiClient.get<FigureItem[]>('/api/figures/list');
  },
};
