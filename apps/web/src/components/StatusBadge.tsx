const STYLES: Record<string, string> = {
  PASS: 'bg-green-100 text-green-800 border-green-200',
  WARN: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  FAIL: 'bg-red-100 text-red-800 border-red-200',
  pending: 'bg-gray-100 text-gray-600 border-gray-200',
  imported: 'bg-blue-100 text-blue-700 border-blue-200',
  failed: 'bg-red-100 text-red-700 border-red-200',
};

interface Props {
  status: string;
  size?: 'sm' | 'md';
}

export default function StatusBadge({ status, size = 'sm' }: Props) {
  const style = STYLES[status] ?? 'bg-gray-100 text-gray-600 border-gray-200';
  const px = size === 'md' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs';
  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${px} ${style}`}>
      {status}
    </span>
  );
}
