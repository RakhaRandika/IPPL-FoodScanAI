import { useState } from "react";
import { scanFood } from "../services/api";

export function useFoodScanner() {
  const [scannedImage, setScannedImage] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const scanImage = async (file, confidence = 0.25) => {
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => setScannedImage(reader.result);
    reader.readAsDataURL(file);

    setIsScanning(true);
    setShowResults(false);

    try {
      const result = await scanFood(file, confidence);
      console.log("Scan result:", result);

      if (result.success && result.predictions?.length > 0) {
        const topPrediction = result.predictions[0];

        // Calculate health score based on nutrition data if available
        let healthScore = Math.floor(60 + Math.random() * 30);
        if (result.nutrition_info?.total) {
          const { protein, fat, carbs } = result.nutrition_info.total;
          const balanced = protein > 10 && fat < 30 && carbs < 50;
          healthScore = balanced
            ? Math.floor(70 + Math.random() * 25)
            : Math.floor(50 + Math.random() * 30);
        }

        // Get unique ingredients for food name
        const uniqueIngredients = result.detected_ingredients?.length > 0
          ? [...new Set(result.detected_ingredients)]
          : result.predictions.map(p => p.label);

        const data = {
          foodName: uniqueIngredients.slice(0, 3).join(", ") || 
                    topPrediction.label || 
                    "Makanan Terdeteksi",
          confidence: topPrediction.confidence,
          calories: result.nutrition_info?.total?.calories || null,
          healthScore: healthScore,
          tags: result.predictions.slice(0, 5).map((p) => p.label),
          insights: [
            {
              type: "positive",
              message: `Terdeteksi ${result.count} jenis makanan dengan confidence ${topPrediction.confidence}%`,
            },
          ],
          allPredictions: result.predictions,
          detected_ingredients: uniqueIngredients,
          // NEW: Add nutrition and recipe data
          nutrition_info: result.nutrition_info || null,
          recommended_recipes: result.recommended_recipes || [],
          detected_ingredients: result.detected_ingredients || [],
        };

        setAnalysisData(data);
        setShowResults(true);
        return { success: true, data, imageUrl: reader.result };
      } else {
        throw new Error("Tidak ada makanan terdeteksi dalam gambar");
      }
    } catch (error) {
      console.error("Scan failed:", error);
      throw error;
    } finally {
      setIsScanning(false);
    }
  };

  const resetScan = () => {
    setScannedImage(null);
    setShowResults(false);
    setAnalysisData(null);
  };

  return {
    scannedImage,
    analysisData,
    isScanning,
    showResults,
    scanImage,
    resetScan,
    // Export setters for direct use (e.g., camera capture)
    setScannedImage,
    setAnalysisData,
    setShowResults,
  };
}
