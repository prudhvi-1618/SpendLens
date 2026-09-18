import { useState, useEffect, useCallback } from "react";
import { fetchAnomalies } from "../api/insights";

export const useAnomalies = () => {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAnomalies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAnomalies();
      setAnomalies(data || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load anomalies");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnomalies();
  }, [loadAnomalies]);

  return { anomalies, loading, error, refetch: loadAnomalies };
};
