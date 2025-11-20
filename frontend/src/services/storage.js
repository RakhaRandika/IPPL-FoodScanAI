const STORAGE_KEYS = {
  RECENT_SCANS: "recentScans",
};

export const storageService = {
  getRecentScans() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.RECENT_SCANS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error("Error reading from localStorage:", e);
      return [];
    }
  },

  saveRecentScans(scans) {
    try {
      localStorage.setItem(STORAGE_KEYS.RECENT_SCANS, JSON.stringify(scans));
    } catch (e) {
      console.error("Error saving to localStorage:", e);
    }
  },

  clearRecentScans() {
    try {
      localStorage.removeItem(STORAGE_KEYS.RECENT_SCANS);
    } catch (e) {
      console.error("Error clearing localStorage:", e);
    }
  },
};
