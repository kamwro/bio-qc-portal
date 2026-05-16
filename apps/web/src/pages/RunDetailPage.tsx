import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQCSummary, useRun } from '../api/runs';
import { useSamples } from '../api/samples';
import ImportForm from '../components/ImportForm';
import QCCharts from '../components/QCCharts';
import SampleTable from '../components/SampleTable';
import StatusBadge from '../components/StatusBadge';
import { useProject } from '../api/projects';

type Tab = 'import' | 'samples' | 'charts';

function SummaryCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function RunDetailPage() {
  const { projectId, runId } = useParams<{ projectId: string; runId: string }>();
  const { data: project } = useProject(projectId!);
  const { data: run, isLoading } = useRun(runId!);
  const { data: summary } = useQCSummary(runId!);
  const { data: samples } = useSamples(runId!);

  const hasData = (summary?.total_samples ?? 0) > 0;
  const [tab, setTab] = useState<Tab>(hasData ? 'samples' : 'import');

  if (isLoading) return <p className="text-gray-400 text-sm">Loading…</p>;
  if (!run) return <p className="text-red-600 text-sm">Run not found.</p>;

  const handleImportSuccess = () => setTab('samples');

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-400 mb-6">
        <Link to="/" className="hover:text-indigo-600 transition-colors">
          Projects
        </Link>
        <span>/</span>
        <Link to={`/projects/${projectId}`} className="hover:text-indigo-600 transition-colors">
          {project?.name ?? projectId}
        </Link>
        <span>/</span>
        <span className="text-gray-700 font-medium">{run.name}</span>
      </nav>

      {/* Run header */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{run.name}</h1>
            <p className="text-sm text-gray-500 mt-0.5">{run.platform}</p>
          </div>
          <StatusBadge status={run.status} size="md" />
        </div>
        <p className="text-xs text-gray-400 mt-2">
          {new Date(run.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Summary cards — only when data exists */}
      {hasData && summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
          <SummaryCard label="Total" value={summary.total_samples} />
          <SummaryCard label="PASS" value={summary.pass_count} sub={`${summary.pass_rate}%`} />
          <SummaryCard label="WARN" value={summary.warn_count} />
          <SummaryCard label="FAIL" value={summary.fail_count} />
          <SummaryCard label="Avg Q30" value={`${summary.avg_q30_score}%`} />
          <SummaryCard label="Avg GC" value={`${summary.avg_gc_content}%`} />
          <SummaryCard label="Avg Dup" value={`${summary.avg_duplication_rate}%`} />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        {(
          [
            { key: 'import', label: 'Import' },
            { key: 'samples', label: 'Samples', disabled: !hasData },
            { key: 'charts', label: 'Charts', disabled: !hasData },
          ] as { key: Tab; label: string; disabled?: boolean }[]
        ).map(({ key, label, disabled }) => (
          <button
            key={key}
            disabled={disabled}
            onClick={() => setTab(key)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
              tab === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'import' && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Import QC data</h2>
          <p className="text-sm text-gray-500 mb-5">
            Paste a JSON payload containing sample metrics. See{' '}
            <code className="bg-gray-100 px-1 rounded text-xs">samples/qc_metrics.json</code> for
            the expected format, or use <strong>make api-seed</strong> to load the demo dataset.
          </p>
          <ImportForm runId={runId!} onSuccess={handleImportSuccess} />
        </div>
      )}

      {tab === 'samples' && samples && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-4">Samples ({samples.length})</h2>
          <SampleTable samples={samples} />
        </div>
      )}

      {tab === 'charts' && samples && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-4">QC charts</h2>
          <QCCharts samples={samples} />
        </div>
      )}
    </div>
  );
}
