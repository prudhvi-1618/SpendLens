import { useState, useEffect, useCallback } from "react";
import { fetchTransactions } from "../api/insights";

export const useTransactions = (filters) => {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTransactions(filters);
      setTransactions(data.items || []);
      setTotal(data.total || 0);
      setPage(data.page || 1);
      setPages(data.pages || 1);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load transactions");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  return { transactions, total, page, pages, loading, error, refetch: loadTransactions };
};
