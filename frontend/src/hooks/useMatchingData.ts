/**
 * React Query Hooks for Thesis Allocation Decision Support
 */
import { useQuery, useMutation } from '@tanstack/react-query';
import { matchingApi } from '../services/api/matching';
import type {
  DatasetSplit,
  MatchCohortRequest,
  RecommendRequest,
} from '../types/api';

export const QUERY_KEYS = {
  overview: ['matching', 'overview'] as const,
  benchmarks: ['matching', 'benchmarks'] as const,
  trainingCurves: ['matching', 'trainingCurves'] as const,
  advisors: ['matching', 'advisors'] as const,
  theses: (split: DatasetSplit) => ['matching', 'theses', split] as const,
  figures: ['matching', 'figures'] as const,
};

export function useOverview() {
  return useQuery({
    queryKey: QUERY_KEYS.overview,
    queryFn: matchingApi.getOverview,
    staleTime: 60 * 1000,
  });
}

export function useBenchmarks() {
  return useQuery({
    queryKey: QUERY_KEYS.benchmarks,
    queryFn: matchingApi.getBenchmarks,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTrainingCurves() {
  return useQuery({
    queryKey: QUERY_KEYS.trainingCurves,
    queryFn: matchingApi.getTrainingCurves,
    staleTime: 10 * 60 * 1000,
  });
}

export function useAdvisors() {
  return useQuery({
    queryKey: QUERY_KEYS.advisors,
    queryFn: matchingApi.getAdvisors,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTheses(split: DatasetSplit = 'validation', limit: number = 50) {
  return useQuery({
    queryKey: QUERY_KEYS.theses(split),
    queryFn: () => matchingApi.getTheses(split, limit),
    staleTime: 2 * 60 * 1000,
  });
}

export function useFigures() {
  return useQuery({
    queryKey: QUERY_KEYS.figures,
    queryFn: matchingApi.getFigures,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCohortMatchMutation() {
  return useMutation({
    mutationFn: (req: MatchCohortRequest) => matchingApi.matchCohort(req),
  });
}

export function useRecommendMutation() {
  return useMutation({
    mutationFn: (req: RecommendRequest) => matchingApi.recommendAdvisor(req),
  });
}
