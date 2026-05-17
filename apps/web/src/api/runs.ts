import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ImportRequest, QCSummary, RunReport, SequencingRun } from '../types';
import { apiClient } from './client';

export function useRun(runId: string) {
  return useQuery<SequencingRun>({
    queryKey: ['runs', runId],
    queryFn: () => apiClient.get(`/runs/${runId}`).then((r) => r.data),
    enabled: !!runId,
  });
}

export function useQCSummary(runId: string) {
  return useQuery<QCSummary>({
    queryKey: ['runs', runId, 'qc-summary'],
    queryFn: () => apiClient.get(`/runs/${runId}/qc-summary`).then((r) => r.data),
    enabled: !!runId,
  });
}

export function useRunReport(runId: string) {
  return useQuery<RunReport>({
    queryKey: ['runs', runId, 'report'],
    queryFn: () => apiClient.get(`/runs/${runId}/report`).then((r) => r.data),
    enabled: !!runId,
  });
}

export function useImportSamples(runId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: ImportRequest) =>
      apiClient.post(`/runs/${runId}/import`, body).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['runs', runId] });
      qc.invalidateQueries({ queryKey: ['runs', runId, 'samples'] });
      qc.invalidateQueries({ queryKey: ['runs', runId, 'qc-summary'] });
    },
  });
}

export function useImportFiles(runId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) =>
      apiClient
        .post(`/runs/${runId}/import/files`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['runs', runId] });
      qc.invalidateQueries({ queryKey: ['runs', runId, 'samples'] });
      qc.invalidateQueries({ queryKey: ['runs', runId, 'qc-summary'] });
    },
  });
}
