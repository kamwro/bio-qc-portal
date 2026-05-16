import { Link, useParams } from 'react-router-dom';
import { useSample } from '../api/samples';
import StatusBadge from '../components/StatusBadge';

function MetricRow({
  label,
  value,
  unit,
  note,
}: {
  label: string;
  value: number;
  unit?: string;
  note?: string;
}) {
  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-3 pr-4 text-sm font-medium text-gray-700 w-48">{label}</td>
      <td className="py-3 text-sm text-gray-900 font-mono">
        {value.toLocaleString()}
        {unit && <span className="text-gray-400 ml-1">{unit}</span>}
      </td>
      {note && <td className="py-3 pl-4 text-xs text-gray-400">{note}</td>}
    </tr>
  );
}

const THRESHOLD_NOTES: Record<string, string> = {
  q30_score: 'PASS ≥ 80%  ·  WARN ≥ 70%  ·  FAIL < 70%',
  gc_content: 'PASS 40–60%  ·  WARN 35–65%  ·  FAIL outside',
  duplication_rate: 'PASS <= 20%  ·  WARN <= 50%  ·  FAIL > 50%',
  adapter_content: 'PASS ≤ 5%  ·  WARN ≤ 10%  ·  FAIL > 10%',
};

export default function SampleDetailPage() {
  const { sampleId } = useParams<{ sampleId: string }>();
  const { data: sample, isLoading } = useSample(sampleId!);

  if (isLoading) return <p className="text-gray-400 text-sm">Loading…</p>;
  if (!sample) return <p className="text-red-600 text-sm">Sample not found.</p>;

  const m = sample.qc_metric;

  return (
    <div className="max-w-2xl">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-400 mb-6">
        <Link to="/" className="hover:text-indigo-600 transition-colors">
          Projects
        </Link>
        <span>/</span>
        <span className="text-gray-500">…</span>
        <span>/</span>
        <span className="text-gray-700 font-medium">{sample.sample_name}</span>
      </nav>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{sample.sample_name}</h1>
            {sample.external_id && (
              <p className="text-sm text-gray-400 mt-0.5">External ID: {sample.external_id}</p>
            )}
          </div>
          {m && <StatusBadge status={m.qc_status} size="md" />}
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Imported {new Date(sample.created_at).toLocaleDateString()}
        </p>
      </div>

      {!m && <p className="text-gray-400 text-sm">No QC metrics available for this sample.</p>}

      {m && (
        <>
          {/* QC Metrics */}
          <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">QC metrics</h2>
            <table className="w-full">
              <tbody>
                <MetricRow label="Total reads" value={m.total_reads} note="Raw read count" />
                <MetricRow
                  label="Q30 score"
                  value={m.q30_score}
                  unit="%"
                  note={THRESHOLD_NOTES.q30_score}
                />
                <MetricRow
                  label="GC content"
                  value={m.gc_content}
                  unit="%"
                  note={THRESHOLD_NOTES.gc_content}
                />
                <MetricRow
                  label="Duplication rate"
                  value={m.duplication_rate}
                  unit="%"
                  note={THRESHOLD_NOTES.duplication_rate}
                />
                <MetricRow
                  label="Adapter content"
                  value={m.adapter_content}
                  unit="%"
                  note={THRESHOLD_NOTES.adapter_content}
                />
                <MetricRow
                  label="Mean read quality"
                  value={m.mean_read_quality}
                  note="Phred-scaled"
                />
              </tbody>
            </table>
          </div>

          {/* Status explanation */}
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-3">
              Status: <StatusBadge status={m.qc_status} size="md" />
            </h2>
            <ul className="space-y-2 text-sm">
              <StatusLine
                label="Q30 score"
                value={m.q30_score}
                pass={m.q30_score >= 80}
                warn={m.q30_score >= 70}
                unit="%"
              />
              <StatusLine
                label="GC content"
                value={m.gc_content}
                pass={m.gc_content >= 40 && m.gc_content <= 60}
                warn={m.gc_content >= 35 && m.gc_content <= 65}
                unit="%"
              />
              <StatusLine
                label="Duplication rate"
                value={m.duplication_rate}
                pass={m.duplication_rate <= 20}
                warn={m.duplication_rate <= 50}
                unit="%"
                invertBetter
              />
              <StatusLine
                label="Adapter content"
                value={m.adapter_content}
                pass={m.adapter_content <= 5}
                warn={m.adapter_content <= 10}
                unit="%"
                invertBetter
              />
            </ul>
          </div>
        </>
      )}
    </div>
  );
}

function StatusLine({
  label,
  value,
  pass,
  warn,
  unit,
  invertBetter,
}: {
  label: string;
  value: number;
  pass: boolean;
  warn: boolean;
  unit?: string;
  invertBetter?: boolean;
}) {
  const status = pass ? 'PASS' : warn ? 'WARN' : 'FAIL';
  const color = pass ? 'text-green-700' : warn ? 'text-yellow-700' : 'text-red-700';
  const icon = pass ? '✓' : warn ? '!' : '✗';
  void invertBetter;
  return (
    <li className="flex items-center gap-3">
      <span className={`font-bold ${color}`}>{icon}</span>
      <span className="text-gray-600 w-40">{label}</span>
      <span className="font-mono text-gray-800">
        {value.toFixed(1)}
        {unit}
      </span>
      <StatusBadge status={status} />
    </li>
  );
}
