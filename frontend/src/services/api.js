// Service untuk berkomunikasi dengan Backend API
// File: src/services/api.js

// Use relative URL (akan otomatis pakai domain yang sama)
const API_BASE_URL =
  window.location.hostname === "localhost" ? "http://localhost:8000" : ""; // Empty string = relative URL, akan jadi foodscan.healthify.cloud/api

/**
 * Scan/deteksi makanan dari gambar
 * @param {File} imageFile - File gambar
 * @param {number} confidence - Threshold confidence (0-1)
 * @returns {Promise} Response dari API
 */
export const scanFood = async (imageFile, confidence = 0.25) => {
  try {
    const formData = new FormData();
    formData.append("file", imageFile);
    formData.append("confidence", confidence);

    const response = await fetch(`${API_BASE_URL}/api/scan`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Gagal melakukan scan");
    }

    return await response.json();
  } catch (error) {
    console.error("Error scanning food:", error);
    throw error;
  }
};

/**
 * Cek status health backend
 * @returns {Promise} Status health
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scan/health`);
    return await response.json();
  } catch (error) {
    console.error("Error checking health:", error);
    throw error;
  }
};

/**
 * Get nutrition info untuk ingredient
 * @param {string} ingredient - Nama ingredient
 * @returns {Promise} Nutrition info
 */
export const getNutrition = async (ingredient) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/nutrition/${ingredient}`);

    if (!response.ok) {
      throw new Error("Nutrition info not found");
    }

    return await response.json();
  } catch (error) {
    console.error("Error getting nutrition:", error);
    throw error;
  }
};

/**
 * Get nutrition info untuk multiple ingredients (batch)
 * @param {Array<string>} ingredients - Array of ingredient names
 * @returns {Promise} Batch nutrition info
 */
export const getNutritionBatch = async (ingredients) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/nutrition/batch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ingredients }),
    });

    if (!response.ok) {
      throw new Error("Failed to get nutrition info");
    }

    return await response.json();
  } catch (error) {
    console.error("Error getting batch nutrition:", error);
    throw error;
  }
};

/**
 * Get list of known ingredients
 * @returns {Promise} List of ingredients
 */
export const getKnownIngredients = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/nutrition/known`);
    return await response.json();
  } catch (error) {
    console.error("Error getting known ingredients:", error);
    throw error;
  }
};

/**
 * Get recipe recommendations based on ingredients
 * @param {Array<string>} ingredients - Array of ingredient names
 * @returns {Promise} Recipe recommendations
 */
export const getRecipeRecommendations = async (ingredients) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recipes/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ingredients }),
    });

    if (!response.ok) {
      throw new Error("Failed to get recipe recommendations");
    }

    return await response.json();
  } catch (error) {
    console.error("Error getting recipe recommendations:", error);
    throw error;
  }
};

/**
 * Search recipes by name
 * @param {string} query - Search query
 * @returns {Promise} Search results
 */
export const searchRecipes = async (query) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/recipes/search?query=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
      throw new Error("Failed to search recipes");
    }

    return await response.json();
  } catch (error) {
    console.error("Error searching recipes:", error);
    throw error;
  }
};

/**
 * Get camera stream URL
 * @returns {string} Camera stream URL
 */
export const getCameraStreamUrl = () => {
  return `${API_BASE_URL}/camera/stream`;
};

/**
 * Get camera detection stream URL
 * @param {number} confidence - Detection confidence threshold
 * @returns {string} Camera detection stream URL
 */
export const getCameraDetectionStreamUrl = (confidence = 0.15) => {
  return `${API_BASE_URL}/camera/stream/detect?confidence=${confidence}`;
};

/**
 * Capture and scan from camera
 * @param {number} confidence - Detection confidence threshold
 * @returns {Promise} Scan results
 */
export const captureCameraScan = async (confidence = 0.15) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/camera/capture/scan?confidence=${confidence}`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error("Failed to capture and scan from camera");
    }

    return await response.json();
  } catch (error) {
    console.error("Error capturing camera scan:", error);
    throw error;
  }
};

/**
 * Get camera status
 * @returns {Promise} Camera status
 */
export const getCameraStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/camera/status`);
    return await response.json();
  } catch (error) {
    console.error("Error getting camera status:", error);
    throw error;
  }
};

const api = {
  scanFood,
  checkHealth,
  getNutrition,
  getNutritionBatch,
  getKnownIngredients,
  getRecipeRecommendations,
  searchRecipes,
  getCameraStreamUrl,
  getCameraDetectionStreamUrl,
  captureCameraScan,
  getCameraStatus,
};

export default api;
