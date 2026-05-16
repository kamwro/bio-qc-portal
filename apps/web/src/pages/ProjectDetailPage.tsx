import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useProject, useRuns } from '../api/projects';
import CreateRunModal from '../components/CreateRunModal';
import StatusBadge from '../components/StatusBadge';

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project, isLoading: loadingProject } = useProject(projectId!);
  const { data: runs, isLoading: loadingRuns } = useRuns(projectId!);
  const [showModal, setShowModal] = useState(false);

  if (loadingProject) return <p className="text-gray-400 text-sm">Loading…</p>;
  if (!project) return <p className="text-red-600 text-sm">Project not found.</p>;

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-400 mb-6">
        <Link to="/" className="hover:text-indigo-600 transition-colors">
          Projects
        </Link>
        <span>/</span>
        <span className="text-gray-700 font-medium">{project.name}</span>
      </nav>

      {/* Project header */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <h1 className="text-xl font-bold text-gray-900">{project.name}</h1>
        {project.description && <p className="text-sm text-gray-500 mt-1">{project.description}</p>}
        <p className="text-xs text-gray-400 mt-2">
          Created {new Date(project.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Runs section */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Sequencing runs</h2>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + New run
        </button>
      </div>

      {loadingRuns && <p className="text-gray-400 text-sm">Loading runs…</p>}

      {runs && runs.length === 0 && (
        <div className="text-center py-12 border-2 border-dashed border-gray-200 rounded-xl">
          <p className="text-gray-400 font-medium">No runs yet</p>
          <p className="text-gray-300 text-sm mt-1">
            Create a sequencing run to start importing QC data
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            + New run
          </button>
        </div>
      )}

      {runs && runs.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {runs.map((r) => (
            <Link
              key={r.id}
              to={`/projects/${projectId}/runs/${r.id}`}
              className="block bg-white border border-gray-200 rounded-xl p-5 hover:border-indigo-300 hover:shadow-sm transition-all group"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                  {r.name}
                </h3>
                <StatusBadge status={r.status} />
              </div>
              <p className="text-sm text-gray-500 mt-1">{r.platform}</p>
              <p className="text-xs text-gray-400 mt-3">
                {new Date(r.created_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      )}

      {showModal && <CreateRunModal projectId={projectId!} onClose={() => setShowModal(false)} />}
    </div>
  );
}
