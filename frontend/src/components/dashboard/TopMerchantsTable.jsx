export default function TopMerchantsTable({ byMerchant }) {
  if (!byMerchant) return null;

  const entries = Object.entries(byMerchant).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const totalSpend = entries.reduce((sum, [_, amount]) => sum + amount, 0) || 1; // avoid div by 0

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">Top Merchants</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-800/50">
            <tr>
              <th className="px-4 py-3 text-sm font-medium text-slate-400 rounded-l-lg">Rank</th>
              <th className="px-4 py-3 text-sm font-medium text-slate-400">Merchant</th>
              <th className="px-4 py-3 text-sm font-medium text-slate-400 text-right">Amount</th>
              <th className="px-4 py-3 text-sm font-medium text-slate-400 rounded-r-lg w-1/3">Share of Total</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([merchant, amount], idx) => {
              const percentage = ((amount / totalSpend) * 100).toFixed(1);
              return (
                <tr key={merchant} className="border-b border-slate-800/50 hover:bg-slate-800/25 transition-colors">
                  <td className="px-4 py-4 text-sm text-slate-500 whitespace-nowrap">#{idx + 1}</td>
                  <td className="px-4 py-4 text-sm font-medium text-slate-100 whitespace-nowrap">{merchant}</td>
                  <td className="px-4 py-4 text-sm font-mono text-indigo-300 text-right whitespace-nowrap">
                    ₹{amount.toLocaleString("en-IN")}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-indigo-600 rounded-full" 
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400 w-10 text-right">{percentage}%</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
