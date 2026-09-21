/**
 * API Type Definitions for Thesis Matching Decision Support Platform
 */

export type DatasetSplit = 'validation' | 'test' | 'train';

export type AllocationAlgorithm =
  | 'exact'
  | 'ppo_maskable'
  | 'ppo'
  | 'gale_shapley'
  | 'greedy'
  | 'random';

export interface OverviewResponse {
  total_theses: number;
  total_advisors: number;
  splits: {
    train: number;
    validation: number;
    test: number;
  };
  promoted_engine: string;
  promoted_reason: string;
  top_rl_engine: string;
  top_rl_steps: number;
  top_rl_compatibility: number;
  seed: number;
}

export interface BenchmarkItem {
  algorithm: string;
  total_reward?: number;
  mean_compatibility: number;
  constraint_violations: number;
  gini_index: number;
  execution_time_ms: number;
  accuracy_vs_historical?: number;
}

export interface TrainingCurvePoint {
  milestone: number;
  train_reward: number;
  val_reward: number;
  train_compatibility: number;
  val_compatibility: number;
  invalid_proposals: number;
}

export type TrainingCurvesResponse = Record<string, TrainingCurvePoint[]>;

export interface Advisor {
  advisor_id: string;
  advisor_name: string;
  academic_title: string;
  primary_field: string;
  email: string;
  capacity: number;
  skill_count: number;
  publication_count: number;
  skills: string[];
}

export interface Thesis {
  student_id: string;
  student_name: string;
  thesis_title: string;
  field_category: string;
  completion_year: number;
  advisor_name_historical: string;
  tech_stack: string[];
}

export interface MatchCohortRequest {
  split: DatasetSplit;
  algorithm: AllocationAlgorithm;
}

export interface CohortAssignment {
  step: number;
  student_id: string;
  student_name: string;
  thesis_title: string;
  field_category: string;
  assigned_advisor_id: string;
  assigned_advisor_name: string;
  academic_title: string;
  compatibility_score: number;
  historical_advisor: string;
  historical_match: boolean;
}

export interface AdvisorWorkload {
  advisor_name: string;
  capacity: number;
  assigned: number;
  remaining: number;
  utilization_pct: number;
}

export interface CohortMatchMetrics {
  mean_compatibility: number;
  total_reward?: number;
  constraint_violations: number;
  invalid_proposals: number;
  gini_index: number;
  execution_time_ms: number;
  accuracy_vs_historical?: number;
}

export interface CohortMatchResponse {
  algorithm: string;
  split: string;
  cohort_size: number;
  metrics: CohortMatchMetrics;
  assignments: CohortAssignment[];
  workload_distribution: AdvisorWorkload[];
}

export interface RecommendRequest {
  title: string;
  field?: string;
  tech_stack?: string;
  top_k: number;
}

export interface AdvisorRecommendation {
  rank: number;
  advisor_id: string;
  advisor_name: string;
  academic_title: string;
  primary_field: string;
  compatibility_score: number;
  capacity: number;
  skills: string[];
  email: string;
}

export interface RecommendResponse {
  query: {
    title: string;
    field?: string;
    tech_stack?: string;
  };
  top_k: number;
  recommendations: AdvisorRecommendation[];
}

export interface FigureItem {
  id: string;
  title: string;
  filename: string;
  caption: string;
}

export interface ApiErrorDetail {
  message: string;
  status?: number;
  detail?: string | unknown;
}
