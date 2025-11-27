import { useState } from "react";

export function RecipeCard({ recipe }) {
  const [showIngredients, setShowIngredients] = useState(false);
  const [showSteps, setShowSteps] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow border border-gray-100">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-800 mb-1">
            {recipe.name}
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
              {recipe.category}
            </span>
            <span className="flex items-center gap-1">
              ❤️ {recipe.loves?.toLocaleString() || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Match Info - UPDATED */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-gray-600">Kecocokan Bahan</span>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-green-600">
              {recipe.match_percentage?.toFixed(1) || 0}%
            </span>
            {recipe.main_matched > 0 && (
              <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-semibold">
                ⭐ Bahan Utama Match
              </span>
            )}
          </div>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full transition-all"
            style={{
              width: `${Math.min(recipe.match_percentage || 0, 100)}%`,
            }}
          ></div>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
          <span>✅ {recipe.matched_count} tersedia</span>
          <span>
            ➕ {recipe.missing_count || recipe.missing_ingredients?.length || 0}{" "}
            perlu ditambah
          </span>
        </div>
      </div>

      {/* Matched Ingredients */}
      {recipe.matched_ingredients && recipe.matched_ingredients.length > 0 && (
        <div className="mb-3">
          <p className="text-sm font-medium text-gray-700 mb-2">
            ✅ Bahan yang Kamu Punya ({recipe.matched_ingredients.length}):
          </p>
          <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
            {recipe.matched_ingredients.map((ing, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs"
              >
                {ing}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missing Ingredients - UPDATED TEXT */}
      {recipe.missing_ingredients && recipe.missing_ingredients.length > 0 && (
        <div className="mb-3">
          <p className="text-sm font-medium text-gray-700 mb-2">
            🛒 Belanja Dulu ({recipe.missing_ingredients.length} bahan):
          </p>
          <div className="flex flex-wrap gap-1 max-h-16 overflow-y-auto">
            {recipe.missing_ingredients.slice(0, 6).map((ing, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs"
              >
                {ing}
              </span>
            ))}
            {recipe.missing_ingredients.length > 6 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                +{recipe.missing_ingredients.length - 6}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Semua Bahan Section */}
      <div className="border-t pt-3 mb-2">
        <button
          onClick={() => setShowIngredients(!showIngredients)}
          className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          <span>🧾 Semua Bahan ({recipe.total_ingredients || 0})</span>
          <span className="text-gray-400">{showIngredients ? "▼" : "▶"}</span>
        </button>
        {showIngredients && recipe.all_ingredients && (
          <div className="mt-3 space-y-1.5 max-h-64 overflow-y-auto bg-gray-50 p-3 rounded-lg">
            {recipe.all_ingredients.map((ing, idx) => {
              const isMatched = recipe.matched_ingredients?.includes(ing);
              return (
                <div
                  key={idx}
                  className={`flex items-start gap-2 text-sm p-1.5 rounded transition ${
                    isMatched
                      ? "bg-green-50 text-green-800"
                      : "text-gray-700 hover:bg-white"
                  }`}
                >
                  <span
                    className={`flex-shrink-0 mt-0.5 font-bold ${
                      isMatched ? "text-green-600" : "text-orange-500"
                    }`}
                  >
                    {isMatched ? "✓" : "○"}
                  </span>
                  <span className="flex-1">{ing}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Langkah Memasak */}
      <div className="border-t pt-3 mb-2">
        <button
          onClick={() => setShowSteps(!showSteps)}
          className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          <span>👨‍🍳 Langkah Memasak ({recipe.total_steps || 0})</span>
          <span className="text-gray-400">{showSteps ? "▼" : "▶"}</span>
        </button>
        {showSteps && recipe.instructions && (
          <div className="mt-3 space-y-3 max-h-96 overflow-y-auto">
            {recipe.instructions.map((step, idx) => (
              <div
                key={idx}
                className="flex gap-3 p-2 hover:bg-gray-50 rounded"
              >
                <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-semibold">
                  {idx + 1}
                </span>
                <p className="text-sm text-gray-700 leading-relaxed flex-1">
                  {step}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* View Full Recipe */}
      {recipe.url && (
        <a
          href={recipe.url}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-center mt-3 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
        >
          Lihat Resep Lengkap →
        </a>
      )}
    </div>
  );
}

export default RecipeCard;
