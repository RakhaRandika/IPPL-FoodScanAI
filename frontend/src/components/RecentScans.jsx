import React from "react";

// Komentar: Komponen ini menampilkan riwayat pemindaian.
// Jika riwayat kosong, tampilkan pesan informatif dan tombol untuk mulai pemindaian.

export function RecentScans({
  scans = [],
  onDelete,
  onClearAll,
  onScanClick,
  selectedId,
}) {
  return (
    <div className="card p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-orange-500">⏱</span>
          Riwayat Pemindaian
        </h3>
        {scans.length > 0 ? (
          <button
            className="text-sm text-red-600 hover:underline"
            onClick={() => onClearAll && onClearAll()}
          >
            Hapus Semua
          </button>
        ) : (
          <div className="text-sm text-gray-500">
            Belum ada riwayat pemindaian
          </div>
        )}
      </div>

      <div className="space-y-4">
        {scans.length === 0 ? (
          <div className="py-6 text-center text-gray-600">
            <p className="mb-3">Riwayat kosong — belum ada pemindaian.</p>
            <button
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-emerald-600 text-white text-sm"
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            >
              Pindai makanan sekarang
            </button>
          </div>
        ) : (
          scans.map((item, i) => (
            <div
              key={item.id || i}
              className={`flex items-center justify-between border-b border-gray-100 pb-3 last:border-none hover:bg-gray-50 transition-colors cursor-pointer rounded-lg px-2 py-2 ${
                selectedId === item.id
                  ? "bg-emerald-50 border-l-4 border-l-emerald-500"
                  : ""
              }`}
              onClick={() => onScanClick && onScanClick(item)}
            >
              <div className="flex items-center gap-3">
                <img
                  src={item.imageDataUrl || item.imageUrl || item.img}
                  alt={item.foodName || item.name || "Foto hasil pemindaian"}
                  className="w-12 h-12 rounded-lg object-cover shadow-sm"
                />
                <div>
                  <p className="font-medium text-gray-700">
                    {item.foodName || item.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {item.calories ? `${item.calories} kkal · ` : ""}
                    {item.timestamp || item.time}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="text-sm text-gray-500">Score</div>
                <div className="inline-flex items-center justify-center w-10 h-6 rounded-md bg-emerald-50 text-emerald-700 font-semibold">
                  {item.healthScore || item.score}
                </div>
                <button
                  className="text-sm text-red-600 hover:underline ml-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete && onDelete(item.id);
                  }}
                >
                  Hapus
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
