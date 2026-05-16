import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useImportSamples } from '../api/runs';

const schema = z.object({
  payload: z.string().min(1, 'Paste a JSON payload'),
});

type FormValues = z.infer<typeof schema>;

const EXAMPLE = JSON.stringify(
  {
    samples: [
      {
        sample_name: 'SAMP001',
        external_id: 'EXT-001',
        total_reads: 50000000,
        q30_score: 85.2,
        gc_content: 48.5,
        duplication_rate: 12.3,
        adapter_content: 1.8,
        mean_read_quality: 37.1,
      },
    ],
  },
  null,
  2,
);

interface Props {
  runId: string;
  onSuccess: () => void;
}

export default function ImportForm({ runId, onSuccess }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });
  const importMutation = useImportSamples(runId);
  const [parseError, setParseError] = useState('');

  const onSubmit = (values: FormValues) => {
    setParseError('');
    let parsed;
    try {
      parsed = JSON.parse(values.payload);
    } catch {
      setParseError('Invalid JSON — check the format and try again.');
      return;
    }
    importMutation.mutate(parsed, {
      onSuccess: () => onSuccess(),
      onError: (err: unknown) => {
        const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        setParseError(msg ?? 'Import failed. Check the payload and try again.');
      },
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          JSON payload
          <span className="ml-2 text-xs font-normal text-gray-400">
            — see <code className="bg-gray-100 px-1 rounded">samples/qc_metrics.json</code> for a
            full example
          </span>
        </label>
        <textarea
          {...register('payload')}
          rows={14}
          placeholder={EXAMPLE}
          className="w-full font-mono text-xs border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-y"
        />
        {errors.payload && <p className="text-red-600 text-xs mt-1">{errors.payload.message}</p>}
        {parseError && <p className="text-red-600 text-xs mt-1">{parseError}</p>}
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={importMutation.isPending}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {importMutation.isPending ? 'Importing…' : 'Import samples'}
        </button>
        <button
          type="button"
          onClick={() => setValue('payload', EXAMPLE)}
          className="px-4 py-2 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
        >
          Load example
        </button>
      </div>

      {importMutation.isSuccess && (
        <p className="text-green-700 text-sm font-medium">
          ✓ Imported {(importMutation.data as { imported: number }).imported} samples successfully.
        </p>
      )}
    </form>
  );
}
