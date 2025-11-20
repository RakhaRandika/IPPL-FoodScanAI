import RecipeCard from "./RecipeCard";
import NutritionInfo from "./NutritionInfo";

export const AnalysisResults = ({ data, imageUrl, onRequestRecipe }) => (
  <div className="space-y-6">
    {/* Main Detection Results Card */}
    <div className="card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <img
            src={imageUrl}
            alt={data.foodName}
            className="w-28 h-28 rounded-md object-cover shadow-sm"
          />
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {data.foodName}
            </h2>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm text-gray-500">Akurasi Deteksi:</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-md text-sm font-medium bg-emerald-100 text-emerald-700">
                {data.confidence}%
              </span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-sm text-gray-500">Health Score</div>
          <div className="w-36 h-3 bg-gray-100 rounded-full mt-2 overflow-hidden">
            <div
              className="h-3 rounded-full bg-emerald-500"
              style={{ width: `${data.healthScore}%` }}
            />
          </div>
          <div className="text-sm font-semibold text-gray-700 mt-1">
            {data.healthScore}%
          </div>
        </div>
      </div>

      {/* All Detections */}
      {data.allPredictions && data.allPredictions.length > 1 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Semua Deteksi ({data.allPredictions.length}):
          </h3>
          <div className="space-y-2">
            {data.allPredictions.map((pred, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between bg-white rounded px-3 py-2"
              >
                <span className="text-sm font-medium text-gray-800">
                  {pred.label}
                </span>
                <span className="text-sm text-emerald-600">
                  {pred.confidence}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {data.tags.map((tag, idx) => (
          <span
            key={idx}
            className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-sm"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="space-y-2">
        {data.insights.map((insight, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-md flex items-start gap-3 ${
              insight.type === "positive"
                ? "bg-emerald-50 text-emerald-700"
                : insight.type === "warning"
                ? "bg-white/80 text-yellow-700 border-l-4 border-yellow-400"
                : "bg-blue-50 text-blue-700"
            }`}
          >
            {insight.type === "warning" ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-yellow-500 mt-1 flex-shrink-0"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.68-1.36 3.445 0l5.518 9.81c.75 1.334-.213 2.991-1.722 2.991H4.461c-1.51 0-2.472-1.657-1.722-2.99l5.518-9.811zM11 13a1 1 0 10-2 0 1 1 0 002 0zm-1-2a1 1 0 01-1-1V7a1 1 0 112 0v3a1 1 0 01-1 1z"
                  clipRule="evenodd"
                />
              </svg>
            ) : null}

            <div className="flex-1">
              <div className="text-sm leading-snug">{insight.message}</div>
            </div>
          </div>
        ))}
      </div>
    </div>

    {/* Nutrition Information */}
    {data.nutrition_info && (
      <NutritionInfo nutritionData={data.nutrition_info} />
    )}

    {/* Recipe Recommendations */}
    {data.recommended_recipes && data.recommended_recipes.length > 0 && (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          🍳 Recommended Recipes ({data.recommended_recipes.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.recommended_recipes.map((recipe, idx) => (
            <RecipeCard key={idx} recipe={recipe} />
          ))}
        </div>
      </div>
    )}
  </div>
);
