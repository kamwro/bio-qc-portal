import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useProjects } from '../api/projects';
import CreateProjectModal from '../components/CreateProjectModal';

export default function ProjectsPage() {
  const { data: projects, isLoading, isError } = useProjects();
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Manage research projects and their sequencing runs
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + New project
        </button>
      </div>

      {isLoading && <p className="text-gray-400 text-sm">Loading…</p>}
      {isError && <p className="text-red-600 text-sm">Failed to load projects.</p>}

      {projects && projects.length === 0 && (
        <div className="text-center py-16 border-2 border-dashed border-gray-200 rounded-xl">
          <p className="text-gray-400 font-medium">No projects yet</p>
          <p className="text-gray-300 text-sm mt-1">Create your first project to get started</p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            + New project
          </button>
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <Link
              key={p.id}
              to={`/projects/${p.id}`}
              className="block bg-white border border-gray-200 rounded-xl p-5 hover:border-indigo-300 hover:shadow-sm transition-all group"
            >
              <h2 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                {p.name}
              </h2>
              {p.description && (
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">{p.description}</p>
              )}
              <p className="text-xs text-gray-400 mt-3">
                Created {new Date(p.created_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      )}

      {showModal && <CreateProjectModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
