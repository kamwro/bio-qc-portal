import { useQuery } from '@tanstack/react-query';
import { Sample } from '../types';
import { apiClient } from './client';

export function useSamples(runId: string) {
  return useQuery<Sample[]>({
    queryKey: ['runs', runId, 'samples'],
    queryFn: () => apiClient.get(`/runs/${runId}/samples`).then((r) => r.data),
    enabled: !!runId,
  });
}

export function useSample(sampleId: string) {
  return useQuery<Sample>({
    queryKey: ['samples', sampleId],
    queryFn: () => apiClient.get(`/samples/${sampleId}`).then((r) => r.data),
    enabled: !!sampleId,
  });
}
