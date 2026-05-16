import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Project, SequencingRun } from '../types';
import { apiClient } from './client';

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: () => apiClient.get('/projects').then((r) => r.data),
  });
}

export function useProject(id: string) {
  return useQuery<Project>({
    queryKey: ['projects', id],
    queryFn: () => apiClient.get(`/projects/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; description?: string }) =>
      apiClient.post<Project>('/projects', body).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/projects/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });
}

export function useRuns(projectId: string) {
  return useQuery<SequencingRun[]>({
    queryKey: ['projects', projectId, 'runs'],
    queryFn: () => apiClient.get(`/projects/${projectId}/runs`).then((r) => r.data),
    enabled: !!projectId,
  });
}

export function useCreateRun(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; platform: string }) =>
      apiClient.post<SequencingRun>(`/projects/${projectId}/runs`, body).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects', projectId, 'runs'] }),
  });
}
