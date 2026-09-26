export interface ModelListItem {
  id: string;
  model_ref: string;
  name: string;
  task_type: string;
  domain: string | null;
  current_health: string | null;
  current_health_score: number | null;
  latest_version: string | null;
}

export interface VersionInfo {
  id: string;
  version: string;
  status: string;
  training_date: string;
  baseline_accuracy: number | null;
  baseline_f1: number | null;
  baseline_roc_auc: number | null;
}

export interface FeatureDrift {
  feature: string;
  psi: number;
  ks_pvalue: number;
  js: number;
  level: string;
  training_mean: number | null;
  production_mean: number | null;
}

export interface PredictionDriftInfo {
  js: number;
  level: string;
  previous_distribution: Record<string, number>;
  current_distribution: Record<string, number>;
}

export interface DataQualityInfo {
  null_rate: number;
  outlier_rate: number;
  dup_rate: number;
  issues: { type: string; feature: string; severity: string; detail: string }[];
  score: number;
}

export interface PerformanceInfo {
  accuracy: number | null;
  f1: number | null;
  roc_auc: number | null;
  previous_f1: number | null;
  delta_f1: number | null;
}

export interface MonitoringRunResponse {
  id: string;
  run_ref: string;
  model_id: string;
  model_name: string;
  version: string;
  feature_drift: FeatureDrift[];
  overall_drift_level: string;
  prediction_drift: PredictionDriftInfo | null;
  data_quality: DataQualityInfo;
  performance: PerformanceInfo | null;
  health_score: number;
  health_status: string;
  top_issues: { category: string; feature: string; metric: string; value: number | null; severity: string; detail: string }[];
  recommendation: string | null;
  retraining_recommended: boolean;
  created_at: string;
}

export interface AlertItem {
  id: string;
  model_id: string;
  model_name: string;
  severity: string;
  category: string;
  title: string;
  message: string;
  is_acknowledged: boolean;
  created_at: string;
}

export interface ComparisonRow {
  version: string;
  status: string;
  training_date: string;
  baseline_f1: number | null;
  latest_health_score: number | null;
  latest_overall_drift: string | null;
  retraining_recommended: boolean | null;
}

export interface DashboardData {
  total_models: number;
  healthy: number;
  warning: number;
  critical: number;
  unscored: number;
  active_alerts: number;
  critical_alerts: number;
  recent_alerts: {
    id: string;
    model_name: string;
    severity: string;
    category: string;
    title: string;
    created_at: string;
  }[];
  health_trend: { run_ref: string; health_score: number; created_at: string }[];
}