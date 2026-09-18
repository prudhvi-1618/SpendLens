import { AlertTriangle, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";

export default function TransactionTable({ transactions, total, page, pages, onPageChange, loading }) {
  
  const categoryColors = {
    travel: "bg-blue-900/50 text-blue-400",
    food: "bg-green-900/50 text-green-400",
    subscription: "bg-purple-900/50 text-purple-400",
    utilities: "bg-yellow-900/50 text-yellow-400",
    shopping: "bg-pink-900/50 text-pink-400",
    entertainment: "bg-orange-900/50 text-orange-400",
    healthcare: "bg-teal-900/50 text-teal-400",
    other: "bg-slate-800 text-slate-400"
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-lg flex flex-col">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[800px]">
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Date</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Merchant</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Category</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Amount</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Confidence</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={`skeleton-${i}`} className="animate-pulse">
                  <td className="px-6 py-5"><div className="h-4 bg-slate-800 rounded w-24"></div></td>
                  <td className="px-6 py-5"><div className="h-4 bg-slate-800 rounded w-32"></div></td>
                  <td className="px-6 py-5"><div className="h-6 bg-slate-800 rounded-full w-20"></div></td>
                  <td className="px-6 py-5"><div className="h-4 bg-slate-800 rounded w-16"></div></td>
                  <td className="px-6 py-5"><div className="h-2 bg-slate-800 rounded-full w-24 mt-1"></div></td>
                  <td className="px-6 py-5"><div className="h-4 bg-slate-800 rounded w-20"></div></td>
                </tr>
              ))
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-slate-400 text-sm">
                  No transactions found matching your filters.
                </td>
              </tr>
            ) : (
              transactions.map((tx) => {
                const confPercent = Math.round((tx.confidence || 0) * 100);
                const catColor = categoryColors[tx.category] || categoryColors.other;
                
                return (
                  <tr key={tx.id} className="hover:bg-slate-800/25 transition-colors">
                    <td className="px-6 py-5 text-sm text-slate-400 whitespace-nowrap">
                      {formatDate(tx.date)}
                    </td>
                    <td className="px-6 py-5 text-sm font-medium text-slate-100 whitespace-nowrap">
                      {tx.merchant}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      {tx.category ? (
                        <span className={`text-xs px-2.5 py-1 rounded-full capitalize ${catColor}`}>
                          {tx.category}
                        </span>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-5 text-sm font-mono text-indigo-300 whitespace-nowrap">
                      ₹{tx.amount.toLocaleString("en-IN")}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${confPercent < 70 ? 'bg-amber-500' : 'bg-emerald-500'}`} 
                            style={{ width: `${confPercent}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400">{confPercent}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      {tx.flagged ? (
                        <div className="flex items-center gap-1.5 text-amber-400">
                          <AlertTriangle className="w-4 h-4" />
                          <span className="text-sm font-medium">Flagged</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-emerald-400">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm font-medium">Normal</span>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {!loading && transactions.length > 0 && (
        <div className="px-6 py-4 bg-slate-800/25 border-t border-slate-800 flex items-center justify-between">
          <div className="text-sm text-slate-400">
            Showing <span className="font-medium text-slate-200">{(page - 1) * 20 + 1}</span> to{" "}
            <span className="font-medium text-slate-200">{Math.min(page * 20, total)}</span> of{" "}
            <span className="font-medium text-slate-200">{total}</span> transactions
          </div>
          
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">
              Page {page} of {pages}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
                className="p-1.5 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={() => onPageChange(page + 1)}
                disabled={page >= pages}
                className="p-1.5 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
