import api from './api';
import {
  ModelListItem, MonitoringRunResponse, AlertItem,
  ComparisonRow, DashboardData, VersionInfo
} from '../types';

export const listModels = async (): Promise<ModelListItem[]> => {
  const r = await api.get('/models/');
  return r.data;
};

export const getModel = async (id: string) => {
  const r = await api.get(`/models/${id}`);
  return r.data;
};

export const runMonitoring = async (modelId: string, driftIntensity = 0.3): Promise<MonitoringRunResponse> => {
  const r = await api.post(`/monitoring/models/${modelId}/run`, null, {
    params: { drift_intensity: driftIntensity },
  });
  return r.data;
};

export const getLatestRun = async (modelId: string): Promise<MonitoringRunResponse> => {
  const r = await api.get(`/monitoring/models/${modelId}/latest`);
  return r.data;
};

export const getRunHistory = async (modelId: string) => {
  const r = await api.get(`/monitoring/models/${modelId}/history`);
  return r.data;
};

export const compareVersions = async (modelId: string): Promise<ComparisonRow[]> => {
  const r = await api.get(`/monitoring/models/${modelId}/compare`);
  return r.data;
};

export const listAlerts = async (): Promise<AlertItem[]> => {
  const r = await api.get('/alerts/');
  return r.data;
};

export const acknowledgeAlert = async (id: string): Promise<AlertItem> => {
  const r = await api.post(`/alerts/${id}/acknowledge`);
  return r.data;
};

export const getDashboard = async (): Promise<DashboardData> => {
  const r = await api.get('/analytics/dashboard');
  return r.data;
};