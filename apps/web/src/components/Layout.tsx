import { Link, Outlet, useLocation } from 'react-router-dom';

export default function Layout() {
  const { pathname } = useLocation();
  const onProjects = pathname === '/';

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-6 h-14">
          <Link
            to="/"
            className="flex items-center gap-2 font-semibold text-gray-900 hover:text-indigo-600 transition-colors"
          >
            <span className="text-indigo-600 text-xl">◈</span>
            <span>BioQC Portal</span>
          </Link>
          <nav className="flex items-center gap-1 text-sm">
            <Link
              to="/"
              className={`px-3 py-1.5 rounded-md transition-colors ${
                onProjects
                  ? 'bg-indigo-50 text-indigo-700 font-medium'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Projects
            </Link>
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
