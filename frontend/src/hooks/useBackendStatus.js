import { useState, useEffect, useCallback } from "react";
import { checkHealth } from "../services/api";

export function useBackendStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const probe = useCallback(async () => {
    setLoading(true);
    try {
      const res = await checkHealth();
      console.log("Backend status:", res);
      setStatus(res);
    } catch (err) {
      console.error("Backend tidak tersedia:", err);
      setStatus({ status: "offline", error: err.message });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    probe();
  }, [probe]);

  return { status, loading, retry: probe };
}
