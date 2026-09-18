import { ShieldCheck } from "lucide-react";
import Navbar from "../components/shared/Navbar";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ErrorBanner from "../components/shared/ErrorBanner";
import EmptyState from "../components/shared/EmptyState";
import AlertCard from "../components/anomalies/AlertCard";
import { useAnomalies } from "../hooks/useAnomalies";

export default function AnomaliesPage() {
  const { anomalies, loading, error, refetch } = useAnomalies();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 pt-16">
        <Navbar />
        <main className="h-[calc(100vh-4rem)] flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 pt-16 pb-12">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6">
            <ErrorBanner message={error} onRetry={refetch} />
          </div>
        )}

        {anomalies.length === 0 && !error ? (
          <div className="mt-20">
            <EmptyState 
              icon={ShieldCheck}
              title="No anomalies detected"
              description="Your spending looks normal. We'll alert you here if we spot unusual activity."
            />
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-semibold text-slate-100">Anomaly Alerts</h1>
              <span className="bg-amber-500/10 text-amber-400 text-sm font-medium px-3 py-1 rounded-full">
                {anomalies.length} flagged
              </span>
            </div>
            
            <div className="space-y-4">
              {anomalies.map((a) => (
                <AlertCard key={a.id} anomaly={a} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
