import { useRef, useState } from 'react';
import { useImportFiles } from '../api/runs';

type QCFormat = 'simple_json' | 'multiqc_like';

interface Props {
  runId: string;
  onSuccess: () => void;
}

export default function FileImportForm({ runId, onSuccess }: Props) {
  const [qcFormat, setQcFormat] = useState<QCFormat>('multiqc_like');
  const [error, setError] = useState('');

  const manifestRef = useRef<HTMLInputElement>(null);
  const qcFileRef = useRef<HTMLInputElement>(null);

  const importMutation = useImportFiles(runId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const manifestFile = manifestRef.current?.files?.[0];
    const qcFile = qcFileRef.current?.files?.[0];

    if (!manifestFile) {
      setError('Select a manifest CSV file.');
      return;
    }
    if (!qcFile) {
      setError('Select a QC metrics JSON file.');
      return;
    }

    const formData = new FormData();
    formData.append('manifest_file', manifestFile);
    formData.append('qc_file', qcFile);
    formData.append('qc_format', qcFormat);

    importMutation.mutate(formData, {
      onSuccess: () => onSuccess(),
      onError: (err: unknown) => {
        const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        setError(msg ?? 'Import failed. Check the files and try again.');
      },
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* QC format selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">QC file format</label>
        <div className="flex gap-4">
          {(
            [
              { value: 'multiqc_like', label: 'MultiQC-like JSON', desc: 'samples/multiqc_like_data.json' },
              { value: 'simple_json', label: 'Simple JSON', desc: 'samples/qc_metrics.json' },
            ] as { value: QCFormat; label: string; desc: string }[]
          ).map(({ value, label, desc }) => (
            <label
              key={value}
              className={`flex items-start gap-2 p-3 border rounded-lg cursor-pointer transition-colors ${
                qcFormat === value
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="qc_format"
                value={value}
                checked={qcFormat === value}
                onChange={() => setQcFormat(value)}
                className="mt-0.5"
              />
              <div>
                <span className="text-sm font-medium text-gray-800">{label}</span>
                <p className="text-xs text-gray-400 mt-0.5">
                  Example: <code className="bg-gray-100 px-1 rounded">{desc}</code>
                </p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Manifest file */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Sample manifest{' '}
          <span className="text-xs font-normal text-gray-400">
            — CSV with columns: <code className="bg-gray-100 px-1 rounded">sample_name, organism, assay_type</code>
          </span>
        </label>
        <input
          ref={manifestRef}
          type="file"
          accept=".csv,text/csv"
          className="block w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200"
        />
      </div>

      {/* QC file */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          QC metrics file{' '}
          <span className="text-xs font-normal text-gray-400">— JSON</span>
        </label>
        <input
          ref={qcFileRef}
          type="file"
          accept=".json,application/json"
          className="block w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200"
        />
      </div>

      {error && <p className="text-red-600 text-xs">{error}</p>}

      <button
        type="submit"
        disabled={importMutation.isPending}
        className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        {importMutation.isPending ? 'Importing…' : 'Import files'}
      </button>

      {importMutation.isSuccess && (
        <p className="text-green-700 text-sm font-medium">
          ✓ Imported {(importMutation.data as { imported: number }).imported} samples successfully.
        </p>
      )}
    </form>
  );
}
