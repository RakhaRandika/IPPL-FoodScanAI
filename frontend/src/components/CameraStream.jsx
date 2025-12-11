import { useState, useRef } from "react";
import {
  getCameraDetectionStreamUrl,
  captureCameraScan,
  getCameraStreamUrl,
} from "../services/api";

/**
 * Component untuk live camera detection stream
 */
export function CameraStream({ onCapture, scanImage }) {
  const [isActive, setIsActive] = useState(false);
  const [confidence, setConfidence] = useState(0.15);
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState(null);
  const imgRef = useRef(null);

  const streamUrl = getCameraDetectionStreamUrl(confidence);

  const handleCapture = async () => {
    setIsCapturing(true);
    setError(null);

    try {
      const result = await captureCameraScan(confidence);

      // Process the result with scanImage if provided
      if (result.success && onCapture) {
        // Create a synthetic image URL for the captured frame
        const imageUrl = getCameraStreamUrl();

        // Call onCapture with the result and include the camera stream URL
        const enrichedResult = {
          ...result,
          imageUrl: imageUrl,
        };

        onCapture(enrichedResult);
      }
    } catch (err) {
      setError(err.message || "Failed to capture from camera");
    } finally {
      setIsCapturing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          📷 Deteksi Kamera Langsung
        </h2>
        <button
          onClick={() => setIsActive(!isActive)}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isActive
              ? "bg-red-500 hover:bg-red-600 text-white"
              : "bg-green-500 hover:bg-green-600 text-white"
          }`}
        >
          {isActive ? "Stop Camera" : "Start Camera"}
        </button>
      </div>

      {/* Confidence Slider */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Keyakinan Deteksi: {(confidence * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          min="0.05"
          max="0.50"
          step="0.05"
          value={confidence}
          onChange={(e) => setConfidence(parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>5%</span>
          <span>50%</span>
        </div>
      </div>

      {/* Camera Stream */}
      {isActive ? (
        <div className="relative bg-gray-900 rounded-lg overflow-hidden">
          <img
            ref={imgRef}
            src={streamUrl}
            alt="Camera Stream"
            className="w-full h-auto"
            onError={() => setError("Gagal memuat aliran kamera.")}
          />

          {/* Capture Button Overlay */}
          <div className="absolute bottom-4 left-0 right-0 flex justify-center">
            <button
              onClick={handleCapture}
              disabled={isCapturing}
              className={`px-6 py-3 rounded-full font-medium shadow-lg transition-all ${
                isCapturing
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-500 hover:bg-blue-600 text-white hover:shadow-xl"
              }`}
            >
              {isCapturing ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Capturing...
                </span>
              ) : (
                "📸 Capture & Analyze"
              )}
            </button>
          </div>

          {/* Live Indicator */}
          <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          </div>
        </div>
      ) : (
        <div className="bg-gray-100 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">📷</div>
          <p className="text-gray-600">
            Klik "Mulai Kamera" untuk memulai deteksi langsung
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Kamera akan menampilkan deteksi objek secara real-time dengan kotak
            pembatas
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Tips:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Klik Start Camera → izinkan browser mengakses kamera.</li>
          <li>• Arahkan kamera ke bahan makanan (misal tomat, telur, labu).</li>
          <li>
            • Atur slider kepercayaan deteksi
            <br />
            : 5–15% → mendeteksi banyak objek (lebih sensitif)
            <br />: 25–50% → hanya objek dengan kepercayaan tinggi
          </li>
          <li>
            • Klik "Capture & Analyze" untuk mendapatkan analisis lengkap dengan
            resep
          </li>
        </ul>
      </div>
    </div>
  );
}

export default CameraStream;
