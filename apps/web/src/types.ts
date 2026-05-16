export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface SequencingRun {
  id: string;
  project_id: string;
  name: string;
  platform: string;
  status: 'pending' | 'imported' | 'failed';
  created_at: string;
}

export interface QCMetric {
  id: string;
  sample_id: string;
  total_reads: number;
  q30_score: number;
  gc_content: number;
  duplication_rate: number;
  adapter_content: number;
  mean_read_quality: number;
  qc_status: 'PASS' | 'WARN' | 'FAIL';
}

export interface Sample {
  id: string;
  run_id: string;
  sample_name: string;
  external_id: string | null;
  created_at: string;
  qc_metric: QCMetric | null;
}

export interface QCSummary {
  run_id: string;
  total_samples: number;
  pass_count: number;
  warn_count: number;
  fail_count: number;
  pass_rate: number;
  avg_q30_score: number;
  avg_gc_content: number;
  avg_duplication_rate: number;
}

export interface RunReport {
  run_id: string;
  run_name: string;
  project_id: string;
  generated_at: string;
  total_samples: number;
  pass_count: number;
  warn_count: number;
  fail_count: number;
  avg_q30_score: number;
  avg_gc_content: number;
  avg_duplication_rate: number;
  worst_samples_by_adapter_content: {
    sample_name: string;
    adapter_content: number;
    qc_status: string;
  }[];
}

export interface ImportRequest {
  samples: SampleImportItem[];
}

export interface SampleImportItem {
  sample_name: string;
  external_id?: string;
  total_reads: number;
  q30_score: number;
  gc_content: number;
  duplication_rate: number;
  adapter_content: number;
  mean_read_quality: number;
}
