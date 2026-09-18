import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, CircleDot } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { triggerEmailSync, triggerSync } from "../../api/insights";
import LoadingSpinner from "./LoadingSpinner";

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await triggerEmailSync();
      await triggerSync();
    } catch (error) {
      console.error("Sync failed:", error);
    } finally {
      setIsSyncing(false);
    }
  };

  const navLinks = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Anomalies", path: "/anomalies" },
    { name: "Transactions", path: "/transactions" },
  ];

  return (
    <nav className="fixed top-0 w-full z-50 bg-slate-900 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center gap-2">
              <CircleDot className="w-6 h-6 text-indigo-500" />
              <span className="text-xl font-semibold text-slate-100 tracking-tight">SpendLens</span>
            </Link>
          </div>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => {
              const isActive = location.pathname.startsWith(link.path);
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  className={`py-5 text-sm font-medium transition-colors ${
                    isActive
                      ? "text-indigo-400 border-b-2 border-indigo-400"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {link.name}
                </Link>
              );
            })}
          </div>

          {/* Desktop Right Side */}
          <div className="hidden md:flex items-center gap-4">
            <span className="text-sm text-slate-400">{user?.email}</span>
            <button
              onClick={handleSync}
              disabled={isSyncing}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              {isSyncing ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Syncing…</span>
                </>
              ) : (
                <span>Sync Now</span>
              )}
            </button>
            <button
              onClick={logout}
              className="text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors"
            >
              Logout
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-slate-400 hover:text-slate-200 p-2"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800">
          <div className="px-4 pt-2 pb-4 space-y-1">
            {navLinks.map((link) => {
              const isActive = location.pathname.startsWith(link.path);
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-md text-base font-medium ${
                    isActive ? "bg-slate-800 text-indigo-400" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`}
                >
                  {link.name}
                </Link>
              );
            })}
            <div className="mt-4 pt-4 border-t border-slate-800 space-y-4 px-3">
              <div className="text-sm text-slate-400 truncate">{user?.email}</div>
              <button
                onClick={() => {
                  handleSync();
                  setIsMobileMenuOpen(false);
                }}
                disabled={isSyncing}
                className="w-full flex justify-center items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium px-4 py-2 rounded-lg"
              >
                {isSyncing ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Syncing…</span>
                  </>
                ) : (
                  <span>Sync Now</span>
                )}
              </button>
              <button
                onClick={logout}
                className="w-full text-left text-base font-medium text-slate-400 hover:text-slate-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
