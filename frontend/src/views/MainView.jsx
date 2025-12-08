import { useState } from "react";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import { UploadCard } from "../components/UploadCard";
import { CameraStream } from "../components/CameraStream";
import { AnalysisResults } from "../components/AnalysisResults";
import { RecentScans } from "../components/RecentScans";
import { DetectionInfo } from "../components/DetectionInfo";
import { Button } from "../components/Button";
import { Sparkles, Activity, Zap, Upload, Camera } from "lucide-react";
import { useBackendStatus } from "../hooks/useBackendStatus";
import { useRecentScans } from "../hooks/useRecentScans";
import { useFoodScanner } from "../hooks/useFoodScanner";

export function MainView() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scanMode, setScanMode] = useState("upload");
  const [selectedScanId, setSelectedScanId] = useState(null); // Track selected scan
  const { status: backendStatus } = useBackendStatus();
  const { scans, addScan, deleteScan, clearAll } = useRecentScans();
  const {
    scannedImage,
    analysisData,
    isScanning,
    showResults,
    scanImage,
    resetScan,
    setScannedImage,
    setAnalysisData,
    setShowResults,
  } = useFoodScanner();

  const handleImageSelect = async (file) => {
    try {
      const result = await scanImage(file);
      if (result.success) {
        const scanData = {
          imageDataUrl: result.imageUrl,
          foodName: result.data.foodName,
          calories: result.data.calories,
          healthScore: result.data.healthScore,
          // Simpan seluruh data analisis
          fullAnalysisData: result.data,
        };
        addScan(scanData);
        setSelectedScanId(scanData.id);
      }
    } catch (error) {
      alert(
        "Gagal melakukan scan: " +
          error.message +
          "\n\nPastikan bahan yang dideteksi ada dalam dataset kami:\n" +
          "Daging Sapi, Pare, Labu air, Brokoli, Kubis, Wortel, Kembang Kol, Ayam, " +
          "Telur, Terong, Galunggong, Bawang Putih, Jahe, Bandeng, Bawang Bombay, Pepaya, " +
          "Pechay, Babi, Kentang, Labu Kuning, Sayote, Buncis, Nila, Tomat, kangkung"
      );
    }
  };

  const handleCameraCapture = async (captureResult) => {
    console.log("📸 Camera Capture Result:", captureResult);
    console.log("🍳 Recipes received:", captureResult.recommended_recipes);
    console.log("🥗 Nutrition received:", captureResult.nutrition_info);

    if (captureResult.success && captureResult.predictions?.length > 0) {
      const topPrediction = captureResult.predictions[0];

      let healthScore = Math.floor(60 + Math.random() * 30);
      if (captureResult.nutrition_info?.total) {
        const { protein, fat, carbs } = captureResult.nutrition_info.total;
        const balanced = protein > 10 && fat < 30 && carbs < 50;
        healthScore = balanced
          ? Math.floor(70 + Math.random() * 25)
          : Math.floor(50 + Math.random() * 30);
      }

      const data = {
        foodName: topPrediction.label || "Makanan Terdeteksi",
        confidence: topPrediction.confidence,
        calories: captureResult.nutrition_info?.total?.calories || null,
        healthScore: healthScore,
        tags: captureResult.predictions.slice(0, 5).map((p) => p.label),
        insights: [
          {
            type: "positive",
            message: `Terdeteksi ${captureResult.count} jenis makanan dengan confidence ${topPrediction.confidence}%`,
          },
        ],
        allPredictions: captureResult.predictions,
        nutrition_info: captureResult.nutrition_info || null,
        recommended_recipes: captureResult.recommended_recipes || [],
        detected_ingredients: captureResult.detected_ingredients || [],
      };

      console.log("📊 Final data to display:", data);

      setAnalysisData(data);
      setShowResults(true);

      const imageUrl =
        captureResult.imageUrl || "data:image/png;base64,camera_capture";
      setScannedImage(imageUrl);

      const scanData = {
        imageDataUrl: imageUrl,
        foodName: data.foodName,
        calories: data.calories,
        healthScore: data.healthScore,
        // Simpan seluruh data analisis
        fullAnalysisData: data,
      };
      addScan(scanData);
      setSelectedScanId(scanData.id);
    }
  };

  // Handler untuk klik item riwayat
  const handleScanClick = (scan) => {
    console.log("🔍 Scan clicked:", scan);

    // Set selected scan ID untuk highlight
    setSelectedScanId(scan.id);

    // Tampilkan kembali hasil analisis
    if (scan.fullAnalysisData) {
      setAnalysisData(scan.fullAnalysisData);
    } else {
      // Fallback jika data lama tidak punya fullAnalysisData
      setAnalysisData({
        foodName: scan.foodName,
        calories: scan.calories,
        healthScore: scan.healthScore,
        tags: [],
        insights: [
          {
            type: "info",
            message: "Data analisis lengkap tidak tersedia untuk scan lama",
          },
        ],
        allPredictions: [],
        nutrition_info: null,
        recommended_recipes: [],
      });
    }

    setScannedImage(scan.imageDataUrl);
    setShowResults(true);

    // Scroll ke atas untuk melihat hasil
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleResetScan = () => {
    resetScan();
    setScanMode("upload");
    setSelectedScanId(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50">
      <Header onMenuToggle={() => setMenuOpen((v) => !v)} />
      <Sidebar isOpen={menuOpen} onClose={() => setMenuOpen(false)} />

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Backend Status - Only show if offline */}
          {/* Loading Indicator */}
          {isScanning && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex items-center justify-center gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <div className="text-blue-800">
                    <p className="font-medium">Scanning makanan...</p>
                    <p className="text-sm text-blue-600">
                      Menggunakan AI untuk mendeteksi makanan dalam gambar
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!showResults ? (
            <>
              {/* Mode Selector Tabs */}
              <div className="max-w-4xl mx-auto">
                <div className="flex gap-4 justify-center mb-6">
                  <Button
                    onClick={() => setScanMode("upload")}
                    className={`${
                      scanMode === "upload"
                        ? "bg-gradient-to-r from-emerald-600 to-emerald-500"
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                    }`}
                  >
                    <Upload className="size-4 mr-2" />
                    Upload Gambar
                  </Button>
                  <Button
                    onClick={() => setScanMode("camera")}
                    className={`${
                      scanMode === "camera"
                        ? "bg-gradient-to-r from-blue-600 to-blue-500"
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                    }`}
                  >
                    <Camera className="size-4 mr-2" />
                    Live Camera
                  </Button>
                </div>
              </div>

              <div className="max-w-4xl mx-auto">
                <div className="rounded-2xl p-8 bg-white/40 backdrop-blur-sm border border-gray-100">
                  {scanMode === "upload" ? (
                    <UploadCard onImageSelect={handleImageSelect} />
                  ) : (
                    <CameraStream
                      onCapture={handleCameraCapture}
                      scanImage={scanImage}
                    />
                  )}
                </div>
              </div>

              <div className="max-w-4xl mx-auto">
                <DetectionInfo />
              </div>

              <div className="max-w-4xl mx-auto">
                <RecentScans
                  scans={scans}
                  onDelete={deleteScan}
                  onClearAll={clearAll}
                  onScanClick={handleScanClick}
                  selectedId={selectedScanId}
                />
              </div>

              {/* Feature cards */}
              <div className="max-w-6xl mx-auto mt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <FeatureCard
                    icon={<Activity className="text-emerald-600 w-6 h-6" />}
                    title="AI Canggih"
                    description="Teknologi AI terbaru untuk mengenali lebih dari 25+ jenis makanan"
                    bgColor="bg-emerald-50"
                  />
                  <FeatureCard
                    icon={<Zap className="text-blue-600 w-6 h-6" />}
                    title="Instan"
                    description="Hasil analisis nutrisi lengkap hanya dalam hitungan detik"
                    bgColor="bg-blue-50"
                  />
                  <FeatureCard
                    icon={<Activity className="text-purple-600 w-6 h-6" />}
                    title="Akurat"
                    description="Tingkat akurasi tinggi dengan database 14,945 resep Indonesia"
                    bgColor="bg-purple-50"
                  />
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="flex justify-center">
                <Button
                  onClick={handleResetScan}
                  className="bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white"
                >
                  <Sparkles className="size-4 mr-2" />
                  Pindai Makanan Lain
                </Button>
              </div>

              <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-3">
                  <AnalysisResults
                    data={analysisData}
                    imageUrl={
                      scannedImage ||
                      scans[0]?.imageUrl ||
                      process.env.PUBLIC_URL + "/logo.png"
                    }
                    onRequestRecipe={({ data, imageUrl }) => {
                      const img = scannedImage || imageUrl;
                      if (img) {
                        addScan({
                          imageDataUrl: img,
                          foodName: data?.foodName || "Hasil Pemindaian",
                        });
                      }
                    }}
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </main>

      {/* FOOTER */}
      <footer className="mt-16 py-8 border-t border-border bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© 2025 FoodScan AI. Powered by Artificial Intelligence.</p>
        </div>
      </footer>
    </div>
  );
}

// Helper component
function FeatureCard({ icon, title, description, bgColor }) {
  return (
    <div className="card p-6 flex items-start gap-4">
      <div className={`p-3 rounded-lg ${bgColor}`}>{icon}</div>
      <div>
        <h4 className="font-semibold text-gray-800">{title}</h4>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
    </div>
  );
}
