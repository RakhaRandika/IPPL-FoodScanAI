import { useState, useRef, useEffect } from "react";
import { scanFood } from "../services/api";

/**
 * Component untuk live camera detection menggunakan browser webcam
 */
export function CameraStream({ onCapture }) {
  const [isActive, setIsActive] = useState(false);
  const [confidence, setConfidence] = useState(0.5);
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // Start/stop webcam
  useEffect(() => {
    if (isActive) {
      startWebcam();
    } else {
      stopWebcam();
    }
    return () => stopWebcam();
  }, [isActive]);

  const startWebcam = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
    } catch (err) {
      setError(
        "Tidak dapat mengakses kamera. Pastikan browser memiliki izin kamera."
      );
      setIsActive(false);
    }
  };

  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const handleCapture = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    setIsCapturing(true);
    setError(null);

    try {
      // Capture frame dari video ke canvas
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0);

      // Convert canvas ke blob
      canvas.toBlob(
        async (blob) => {
          try {
            const file = new File([blob], "camera-capture.jpg", {
              type: "image/jpeg",
            });

            // Scan image menggunakan API
            const result = await scanFood(file, confidence);

            if (result && onCapture) {
              onCapture({
                ...result,
                imageUrl: canvas.toDataURL("image/jpeg"),
              });
            }
          } catch (err) {
            setError(err.message || "Gagal memproses gambar dari kamera");
          } finally {
            setIsCapturing(false);
          }
        },
        "image/jpeg",
        0.9
      );
    } catch (err) {
      setError(err.message || "Gagal mengambil gambar dari kamera");
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

      {/* Camera Video Stream */}
      {isActive ? (
        <div className="relative bg-gray-900 rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-auto"
          />

          {/* Hidden canvas untuk capture */}
          <canvas ref={canvasRef} className="hidden" />

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
                  Memproses...
                </span>
              ) : (
                "📸 Ambil & Analisis Gambar"
              )}
            </button>
          </div>

          {/* Live Indicator */}
          <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            LIVE
          </div>
        </div>
      ) : (
        <div className="bg-gray-100 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">📷</div>
          <p className="text-gray-600 font-medium">
            Klik "Start Camera" untuk memulai deteksi
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Browser akan meminta izin akses kamera Anda
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
        <h3 className="font-semibold text-blue-900 mb-2">
          💡 Cara Menggunakan:
        </h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>
            • Klik <strong>Start Camera</strong> dan izinkan akses kamera
            browser
          </li>
          <li>• Arahkan kamera ke bahan makanan yang ingin dideteksi</li>
          <li>• Atur slider confidence (5-50%) sesuai kebutuhan</li>
          <li>
            • Klik <strong>Ambil & Analisis Gambar</strong> untuk mendapat
            rekomendasi resep
          </li>
        </ul>
      </div>
    </div>
  );
}

export default CameraStream;
