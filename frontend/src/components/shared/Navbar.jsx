import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, CircleDot, Loader2, CheckCircle } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { useSync } from "../../context/SyncContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const { 
    isSyncing, 
    syncStatus, 
    startSync, 
    openDetailsModal, 
    totalMailsProcessed 
  } = useSync();

  const handleSyncClick = () => {
    if (syncStatus === "idle" || syncStatus === "error") {
      startSync();
    } else {
      openDetailsModal();
    }
    setIsMobileMenuOpen(false);
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
              onClick={handleSyncClick}
              className={`flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-lg transition-colors ${
                syncStatus === "completed" 
                  ? "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                  : isSyncing 
                    ? "bg-slate-800 text-slate-300 hover:bg-slate-700" 
                    : "bg-indigo-600 hover:bg-indigo-500 text-white"
              }`}
            >
              {isSyncing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : syncStatus === "completed" ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>{totalMailsProcessed} processed</span>
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
                onClick={handleSyncClick}
                className={`w-full flex justify-center items-center gap-2 font-medium px-4 py-2 rounded-lg ${
                  syncStatus === "completed" 
                    ? "bg-emerald-500/10 text-emerald-400"
                    : isSyncing 
                      ? "bg-slate-800 text-slate-300" 
                      : "bg-indigo-600 hover:bg-indigo-500 text-white"
                }`}
              >
                {isSyncing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : syncStatus === "completed" ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>View Results</span>
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
