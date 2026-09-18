import { RefreshCw } from "lucide-react";
import EmptyState from "../shared/EmptyState";

export default function RecurringPaymentsList({ recurring }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">Recurring Payments</h3>
      
      {!recurring || recurring.length === 0 ? (
        <div className="py-8">
          <EmptyState 
            icon={RefreshCw}
            title="No recurring payments found"
            description="Sync more emails to detect subscriptions"
          />
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {recurring.map((merchant) => (
            <div 
              key={merchant} 
              className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-full px-4 py-2"
            >
              <RefreshCw className="w-3 h-3 text-emerald-400 flex-shrink-0" />
              <span className="text-sm font-medium text-slate-200 truncate" title={merchant}>
                {merchant}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
