import { useState, useEffect } from "react";

export default function FilterBar({ filters, onChange }) {
  const [merchantInput, setMerchantInput] = useState(filters.merchant || "");

  // Debounce merchant input
  useEffect(() => {
    const handler = setTimeout(() => {
      if (merchantInput !== filters.merchant) {
        onChange({ ...filters, merchant: merchantInput });
      }
    }, 400);

    return () => clearTimeout(handler);
  }, [merchantInput, filters, onChange]);

  const handleClear = () => {
    setMerchantInput("");
    onChange({ category: "", merchant: "", date_from: "", date_to: "" });
  };

  const hasActiveFilters = filters.category || filters.merchant || filters.date_from || filters.date_to;

  const inputClasses = "bg-slate-800 border border-slate-700 text-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500";

  return (
    <div className="flex flex-wrap items-center gap-4">
      <select
        value={filters.category || ""}
        onChange={(e) => onChange({ ...filters, category: e.target.value })}
        className={inputClasses}
      >
        <option value="">All Categories</option>
        <option value="travel">Travel</option>
        <option value="food">Food</option>
        <option value="subscription">Subscription</option>
        <option value="utilities">Utilities</option>
        <option value="shopping">Shopping</option>
        <option value="entertainment">Entertainment</option>
        <option value="healthcare">Healthcare</option>
        <option value="other">Other</option>
      </select>

      <input
        type="text"
        placeholder="Search merchant…"
        value={merchantInput}
        onChange={(e) => setMerchantInput(e.target.value)}
        className={inputClasses}
      />

      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-400">From</span>
        <input
          type="date"
          value={filters.date_from || ""}
          onChange={(e) => onChange({ ...filters, date_from: e.target.value })}
          className={inputClasses}
        />
      </div>

      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-400">To</span>
        <input
          type="date"
          value={filters.date_to || ""}
          onChange={(e) => onChange({ ...filters, date_to: e.target.value })}
          className={inputClasses}
        />
      </div>

      {hasActiveFilters && (
        <button
          onClick={handleClear}
          className="text-sm font-medium text-slate-400 hover:text-slate-200 px-2 py-2 transition-colors"
        >
          Clear Filters
        </button>
      )}
    </div>
  );
}
