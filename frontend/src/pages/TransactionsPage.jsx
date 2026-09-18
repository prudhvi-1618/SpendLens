import { useState } from "react";
import Navbar from "../components/shared/Navbar";
import ErrorBanner from "../components/shared/ErrorBanner";
import FilterBar from "../components/transactions/FilterBar";
import TransactionTable from "../components/transactions/TransactionTable";
import { useTransactions } from "../hooks/useTransactions";

export default function TransactionsPage() {
  const [filters, setFilters] = useState({
    category: "",
    merchant: "",
    date_from: "",
    date_to: "",
    page: 1,
    limit: 20
  });

  const { transactions, total, page, pages, loading, error, refetch } = useTransactions(filters);

  const handleFilterChange = (newFilters) => {
    // If anything but page changes, reset to page 1. FilterBar passes page:1 when it changes inputs.
    setFilters(newFilters);
  };

  return (
    <div className="min-h-screen bg-slate-950 pt-16 pb-12">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-slate-100 mb-6">Transactions</h1>
          <FilterBar 
            filters={filters} 
            onChange={(newFilters) => handleFilterChange({ ...newFilters, page: 1 })} 
          />
        </div>

        {error && (
          <div className="mb-6">
            <ErrorBanner message={error} onRetry={refetch} />
          </div>
        )}

        <div className="mt-6">
          <TransactionTable
            transactions={transactions}
            total={total}
            page={page}
            pages={pages}
            onPageChange={(p) => setFilters(f => ({ ...f, page: p }))}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}
