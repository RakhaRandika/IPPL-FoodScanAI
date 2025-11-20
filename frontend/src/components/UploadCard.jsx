import React, { useRef, useState } from "react";
import { Upload } from "lucide-react";
import { Button } from "./Button";

export function UploadCard({ onImageSelect }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  function handleFiles(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (onImageSelect) onImageSelect(file);
  }

  return (
    <div className="card p-8">
      <div className="flex flex-col items-center space-y-6">
        <div className="bg-emerald-100 p-4 rounded-full">
          <Upload className="text-emerald-600 w-10 h-10" />
        </div>
        <h2 className="text-2xl font-semibold text-gray-800">
          Pindai Makanan Anda
        </h2>
        <p className="text-gray-500 text-center max-w-md">
          Upload foto makanan atau drag & drop di sini untuk analisis
          Rekomendasi Resep dengan AI
        </p>

        <div className="w-full max-w-lg">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              handleFiles(e.dataTransfer.files);
            }}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition ${
              dragOver
                ? "border-emerald-400 bg-emerald-50"
                : "border-gray-300 hover:border-emerald-300"
            }`}
          >
            <p className="text-gray-600 mb-4">Tarik & lepas gambar di sini</p>
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />
            <Button
              onClick={() => inputRef.current && inputRef.current.click()}
              className="bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white px-6 py-3 text-base"
            >
              <Upload className="size-4 mr-2" />
              Upload Foto
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
