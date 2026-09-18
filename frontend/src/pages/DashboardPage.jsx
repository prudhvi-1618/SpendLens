import { MailOpen } from "lucide-react";
import Navbar from "../components/shared/Navbar";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ErrorBanner from "../components/shared/ErrorBanner";
import EmptyState from "../components/shared/EmptyState";
import StatCards from "../components/dashboard/StatCards";
import CategoryBarChart from "../components/dashboard/CategoryBarChart";
import SpendOverTimeChart from "../components/dashboard/SpendOverTimeChart";
import TopMerchantsTable from "../components/dashboard/TopMerchantsTable";
import RecurringPaymentsList from "../components/dashboard/RecurringPaymentsList";
import AISummaryCard from "../components/dashboard/AISummaryCard";
import { useProfile } from "../hooks/useProfile";
import { triggerEmailSync, triggerSync } from "../api/insights";

export default function DashboardPage() {
  const { profile, loading, error, refetch } = useProfile();

  const handleSync = async () => {
    try {
      await triggerEmailSync();
      await triggerSync();
      // Refetch will be triggered by Navbar sync state or user refresh
      refetch();
    } catch (err) {
      console.error("Initial sync failed", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center">
        <LoadingSpinner size="lg" className="mb-4" />
        <p className="text-slate-400 font-medium text-sm">Analyzing your spending…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 pt-20 px-4">
        <Navbar />
        <div className="max-w-3xl mx-auto mt-8">
          <ErrorBanner message={error} onRetry={refetch} />
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-slate-950 pt-16">
        <Navbar />
        <main className="h-[calc(100vh-4rem)] flex items-center justify-center">
          <EmptyState 
            icon={MailOpen}
            title="No spending data yet"
            description="Sync your Gmail to start analyzing your finances"
            actionLabel="Sync Now"
            onAction={handleSync}
          />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 pt-16 pb-12">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        <StatCards profile={profile} />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CategoryBarChart byCategory={profile.by_category} />
          <SpendOverTimeChart monthlyTotals={profile.monthly_totals} />
        </div>
        
        <AISummaryCard summaryText={profile.summary_text} />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopMerchantsTable byMerchant={profile.by_merchant} />
          <RecurringPaymentsList recurring={profile.recurring} />
        </div>
      </main>
    </div>
  );
}
