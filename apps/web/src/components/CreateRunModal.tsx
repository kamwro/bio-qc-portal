import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useCreateRun } from '../api/projects';

const PLATFORMS = [
  'Illumina NovaSeq 6000',
  'Illumina NovaSeq X',
  'Illumina NextSeq 2000',
  'Illumina MiSeq',
  'Oxford Nanopore PromethION',
  'PacBio Revio',
  'Other',
];

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  platform: z.string().min(1, 'Platform is required'),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  projectId: string;
  onClose: () => void;
}

export default function CreateRunModal({ projectId, onClose }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { platform: PLATFORMS[0] },
  });
  const create = useCreateRun(projectId);

  const onSubmit = (values: FormValues) => {
    create.mutate(values, { onSuccess: onClose });
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-900">New sequencing run</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="p-5 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Run name *</label>
            <input
              {...register('name')}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="e.g. Run-2024-Q1-NovaSeq"
            />
            {errors.name && <p className="text-red-600 text-xs mt-1">{errors.name.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Platform *</label>
            <select
              {...register('platform')}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {PLATFORMS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
            {errors.platform && (
              <p className="text-red-600 text-xs mt-1">{errors.platform.message}</p>
            )}
          </div>
          <div className="flex justify-end gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={create.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {create.isPending ? 'Creating…' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
