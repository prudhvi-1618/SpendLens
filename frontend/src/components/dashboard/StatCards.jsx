import { IndianRupee, Tag, Store, RefreshCw } from "lucide-react";

export default function StatCards({ profile }) {
  if (!profile) return null;

  const topCategory = profile.by_category && Object.keys(profile.by_category).length > 0
    ? Object.entries(profile.by_category).sort((a, b) => b[1] - a[1])[0]
    : ["None", 0];

  const topMerchant = profile.by_merchant && Object.keys(profile.by_merchant).length > 0
    ? Object.entries(profile.by_merchant).sort((a, b) => b[1] - a[1])[0]
    : ["None", 0];

  const cards = [
    {
      label: "Last 90 days",
      value: `₹${(profile.total_spend || 0).toLocaleString("en-IN")}`,
      subtext: "",
      icon: IndianRupee,
      color: "indigo"
    },
    {
      label: "Top Category",
      value: topCategory[0].charAt(0).toUpperCase() + topCategory[0].slice(1),
      subtext: `₹${topCategory[1].toLocaleString("en-IN")}`,
      icon: Tag,
      color: "emerald"
    },
    {
      label: "Top Merchant",
      value: topMerchant[0],
      subtext: `₹${topMerchant[1].toLocaleString("en-IN")}`,
      icon: Store,
      color: "amber"
    },
    {
      label: "Subscriptions tracked",
      value: `${(profile.recurring || []).length} active`,
      subtext: "Recurring payments",
      icon: RefreshCw,
      color: "rose"
    }
  ];

  const colorClasses = {
    indigo: { bg: "bg-indigo-950", icon: "text-indigo-400" },
    emerald: { bg: "bg-emerald-950", icon: "text-emerald-400" },
    amber: { bg: "bg-amber-950", icon: "text-amber-400" },
    rose: { bg: "bg-rose-950", icon: "text-rose-400" }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        const colors = colorClasses[card.color];
        
        return (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm font-medium text-slate-400">
                {card.label}
              </div>
              <div className={`${colors.bg} p-2 rounded-lg`}>
                <Icon className={`w-5 h-5 ${colors.icon}`} />
              </div>
            </div>
            
            <div>
              <div className="text-2xl font-semibold text-slate-100 font-mono">
                {card.value}
              </div>
              {card.subtext && (
                <div className="text-sm font-medium text-slate-400 mt-1">
                  {card.subtext}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
