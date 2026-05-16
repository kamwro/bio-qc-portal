import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Sample } from '../types';
import StatusBadge from './StatusBadge';

type Filter = 'ALL' | 'PASS' | 'WARN' | 'FAIL';

interface Props {
  samples: Sample[];
}

export default function SampleTable({ samples }: Props) {
  const [filter, setFilter] = useState<Filter>('ALL');

  const displayed =
    filter === 'ALL' ? samples : samples.filter((s) => s.qc_metric?.qc_status === filter);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        {(['ALL', 'PASS', 'WARN', 'FAIL'] as Filter[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${
              filter === f
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400 hover:text-indigo-600'
            }`}
          >
            {f}
            {f !== 'ALL' && (
              <span className="ml-1 text-xs opacity-70">
                ({samples.filter((s) => s.qc_metric?.qc_status === f).length})
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              {[
                'Sample',
                'External ID',
                'Total Reads',
                'Q30 (%)',
                'GC (%)',
                'Dup (%)',
                'Adapter (%)',
                'Status',
              ].map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {displayed.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-gray-400">
                  No samples match the selected filter.
                </td>
              </tr>
            )}
            {displayed.map((s) => (
              <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 font-medium text-indigo-600">
                  <Link to={`/samples/${s.id}`} className="hover:underline">
                    {s.sample_name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-gray-500">{s.external_id ?? '—'}</td>
                <td className="px-4 py-3 text-gray-700">
                  {s.qc_metric ? s.qc_metric.total_reads.toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {s.qc_metric ? s.qc_metric.q30_score.toFixed(1) : '—'}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {s.qc_metric ? s.qc_metric.gc_content.toFixed(1) : '—'}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {s.qc_metric ? s.qc_metric.duplication_rate.toFixed(1) : '—'}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {s.qc_metric ? s.qc_metric.adapter_content.toFixed(1) : '—'}
                </td>
                <td className="px-4 py-3">
                  {s.qc_metric ? (
                    <StatusBadge status={s.qc_metric.qc_status} />
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
