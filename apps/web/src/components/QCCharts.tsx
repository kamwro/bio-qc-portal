import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Sample } from '../types';

const STATUS_COLORS: Record<string, string> = {
  PASS: '#22c55e',
  WARN: '#eab308',
  FAIL: '#ef4444',
};

const formatPercentTooltip = (value: unknown, label: string): [string, string] => {
  const numericValue = typeof value === 'number' ? value : Number(value ?? 0);

  return [`${numericValue.toFixed(1)}%`, label];
};

interface Props {
  samples: Sample[];
}

function getMetrics(samples: Sample[]) {
  return samples
    .filter((s) => s.qc_metric !== null)
    .map((s) => ({
      name: s.sample_name.replace(/^SAMP0*/, 'S'),
      fullName: s.sample_name,
      q30: s.qc_metric!.q30_score,
      gc: s.qc_metric!.gc_content,
      dup: s.qc_metric!.duplication_rate,
      adapter: s.qc_metric!.adapter_content,
      status: s.qc_metric!.qc_status,
    }));
}

export default function QCCharts({ samples }: Props) {
  const metrics = getMetrics(samples);

  const statusCounts = ['PASS', 'WARN', 'FAIL'].map((s) => ({
    name: s,
    value: metrics.filter((m) => m.status === s).length,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* QC Status Distribution */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">QC Status Distribution</h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={statusCounts}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ name, value }) => `${name}: ${value}`}
            >
              {statusCounts.map((entry) => (
                <Cell key={entry.name} fill={STATUS_COLORS[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Q30 Score */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Q30 Score (%) by Sample</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={metrics} margin={{ left: -10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
            <Tooltip
              formatter={(value) => formatPercentTooltip(value, 'Q30')}
              labelFormatter={(l) => metrics.find((m) => m.name === l)?.fullName ?? l}
            />
            <ReferenceLine
              y={80}
              stroke="#22c55e"
              strokeDasharray="4 2"
              label={{ value: 'PASS', fill: '#22c55e', fontSize: 10 }}
            />
            <ReferenceLine
              y={70}
              stroke="#eab308"
              strokeDasharray="4 2"
              label={{ value: 'WARN', fill: '#eab308', fontSize: 10 }}
            />
            <Bar dataKey="q30" radius={[3, 3, 0, 0]}>
              {metrics.map((m) => (
                <Cell key={m.name} fill={STATUS_COLORS[m.status]} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* GC Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">GC Content (%) by Sample</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={metrics} margin={{ left: -10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
            <Tooltip
              formatter={(value) => formatPercentTooltip(value, 'GC')}
              labelFormatter={(l) => metrics.find((m) => m.name === l)?.fullName ?? l}
            />
            <ReferenceLine y={40} stroke="#22c55e" strokeDasharray="4 2" />
            <ReferenceLine
              y={60}
              stroke="#22c55e"
              strokeDasharray="4 2"
              label={{ value: 'PASS 40–60', fill: '#22c55e', fontSize: 10 }}
            />
            <Bar dataKey="gc" radius={[3, 3, 0, 0]}>
              {metrics.map((m) => (
                <Cell key={m.name} fill={STATUS_COLORS[m.status]} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Duplication Rate */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Duplication Rate (%) by Sample</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={metrics} margin={{ left: -10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
            <Tooltip
              formatter={(value) => formatPercentTooltip(value, 'Dup')}
              labelFormatter={(l) => metrics.find((m) => m.name === l)?.fullName ?? l}
            />
            <ReferenceLine
              y={20}
              stroke="#22c55e"
              strokeDasharray="4 2"
              label={{ value: 'PASS ≤20', fill: '#22c55e', fontSize: 10 }}
            />
            <ReferenceLine
              y={50}
              stroke="#eab308"
              strokeDasharray="4 2"
              label={{ value: 'WARN <=50', fill: '#eab308', fontSize: 10 }}
            />
            <Bar dataKey="dup" radius={[3, 3, 0, 0]}>
              {metrics.map((m) => (
                <Cell key={m.name} fill={STATUS_COLORS[m.status]} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
