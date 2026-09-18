import { useState, useEffect, useCallback } from "react";
import { fetchProfile } from "../api/insights";

export const useProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProfile();
      // If data is empty or missing key fields, treat as no data yet
      if (!data || data.total_spend === undefined) {
        setProfile(null);
      } else {
        setProfile(data);
      }
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setProfile(null);
      } else {
        setError(err.response?.data?.detail || err.message || "Failed to load profile");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  return { profile, loading, error, refetch: loadProfile };
};
