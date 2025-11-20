/**
 * Component untuk menampilkan informasi nutrisi
 */
export function NutritionInfo({ nutritionData }) {
  if (!nutritionData || !nutritionData.ingredients) {
    return null;
  }

  const { ingredients, total, found_count, not_found } = nutritionData;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        🥗 Nutrition Information
      </h2>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Calories</p>
          <p className="text-2xl font-bold text-red-600">
            {total.calories_kcal?.toFixed(0) || 0}
            <span className="text-sm ml-1">kcal</span>
          </p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Protein</p>
          <p className="text-2xl font-bold text-blue-600">
            {total.protein_g?.toFixed(1) || 0}
            <span className="text-sm ml-1">g</span>
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Fat</p>
          <p className="text-2xl font-bold text-yellow-600">
            {total.fat_g?.toFixed(1) || 0}
            <span className="text-sm ml-1">g</span>
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Carbs</p>
          <p className="text-2xl font-bold text-green-600">
            {total.carbs_g?.toFixed(1) || 0}
            <span className="text-sm ml-1">g</span>
          </p>
        </div>
      </div>

      {/* Individual Ingredients */}
      <div className="mb-4">
        <h3 className="font-semibold text-gray-700 mb-3">
          Per Ingredient (100g each):
        </h3>
        <div className="space-y-3">
          {ingredients.map((item, idx) => (
            <div
              key={idx}
              className="bg-gray-50 p-4 rounded-lg border border-gray-200"
            >
              <h4 className="font-medium text-gray-800 mb-2">{item.name}</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <span className="text-gray-600">Calories: </span>
                  <span className="font-semibold">
                    {item.nutrition_per_100g.calories_kcal} kcal
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Protein: </span>
                  <span className="font-semibold">
                    {item.nutrition_per_100g.protein_g}g
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Fat: </span>
                  <span className="font-semibold">
                    {item.nutrition_per_100g.fat_g}g
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Carbs: </span>
                  <span className="font-semibold">
                    {item.nutrition_per_100g.carbs_g}g
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Not Found Warning */}
      {not_found && not_found.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Note:</strong> Nutrition data not available for:{" "}
            {not_found.join(", ")}
          </p>
        </div>
      )}

      {/* Footer Note */}
      <p className="text-xs text-gray-500 mt-4 text-center">
        * Nilai merupakan perkiraan dan berdasarkan porsi 100g. Total
        diasumsikan 100g untuk setiap bahan.
      </p>
    </div>
  );
}

export default NutritionInfo;
