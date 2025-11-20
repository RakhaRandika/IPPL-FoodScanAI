import { useState, useEffect } from "react";
import { storageService } from "../services/storage";

export function useRecentScans() {
  const [scans, setScans] = useState(() => storageService.getRecentScans());

  useEffect(() => {
    storageService.saveRecentScans(scans);
  }, [scans]);

  const addScan = (scanData) => {
    const newScan = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleString(),
      healthScore: scanData.healthScore ?? Math.floor(60 + Math.random() * 30),
      ...scanData,
    };
    setScans((prev) => [newScan, ...prev].slice(0, 20));
    return newScan;
  };

  const deleteScan = (id) => {
    setScans((prev) => prev.filter((scan) => scan.id !== id));
  };

  const clearAll = () => {
    // eslint-disable-next-line no-restricted-globals
    if (confirm("Hapus semua riwayat pemindaian?")) {
      setScans([]);
    }
  };

  return { scans, addScan, deleteScan, clearAll };
}
