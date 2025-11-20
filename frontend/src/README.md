# Frontend Structure - FoodScanAI

Struktur folder frontend yang profesional dan mudah di-maintenance.

## 📁 Struktur Folder

```
src/
├── components/           # UI Components (Presentational Components)
│   ├── AnalysisResults.jsx
│   ├── Button.jsx
│   ├── DetectionInfo.jsx
│   ├── Header.jsx        # Header aplikasi
│   ├── NutritionCard.jsx
│   ├── RecentScans.jsx
│   ├── Sidebar.jsx       # Sidebar menu
│   └── UploadCard.jsx
│
├── views/                # Pages/Views (Container Components)
│   └── MainView.jsx      # Halaman utama aplikasi
│
├── hooks/                # Custom React Hooks
│   ├── useBackendStatus.js   # Hook untuk status backend
│   ├── useFoodScanner.js     # Hook untuk scanning makanan
│   └── useRecentScans.js     # Hook untuk riwayat scan
│
├── services/             # External Services & API
│   ├── api.js            # API calls ke backend
│   └── storage.js        # localStorage service
│
├── constants/            # Constants & Mock Data
│   └── mockData.js       # Mock data untuk development
│
├── utils/                # Helper functions
│
├── App.jsx               # Root component (entry point)
└── index.jsx             # ReactDOM render
```

## 🎯 Penjelasan Struktur

### **components/**

Berisi komponen UI murni (presentational components) yang hanya menerima props dan menampilkan UI.

- Tidak ada business logic
- Reusable dan testable
- Fokus pada tampilan

### **views/**

Berisi halaman/view utama (container components) yang mengatur state dan business logic.

- Menggunakan custom hooks
- Mengatur data flow
- Orchestration layer

### **hooks/**

Custom hooks untuk memisahkan business logic dari UI.

- `useBackendStatus` - Mengelola status koneksi backend
- `useFoodScanner` - Mengelola proses scanning
- `useRecentScans` - Mengelola riwayat pemindaian

### **services/**

Service layer untuk komunikasi eksternal.

- `api.js` - HTTP requests ke backend API
- `storage.js` - localStorage operations

### **constants/**

Data konstan dan mock data.

- `mockData.js` - Mock data untuk development/testing

### **utils/**

Helper functions dan utilities yang dapat digunakan di seluruh aplikasi.

## 🚀 Keuntungan Struktur Ini

1. **Separation of Concerns** - Logic terpisah dari UI
2. **Reusability** - Components dan hooks dapat digunakan ulang
3. **Testability** - Mudah untuk unit testing
4. **Maintainability** - Mudah untuk maintenance dan scaling
5. **Readability** - Struktur yang jelas dan mudah dipahami
6. **Professional** - Mengikuti best practices React

## 📝 Cara Menambah Fitur Baru

### 1. Tambah Component Baru

```jsx
// src/components/NewComponent.jsx
export function NewComponent({ data }) {
  return <div>{data}</div>;
}
```

### 2. Tambah Custom Hook

```jsx
// src/hooks/useNewFeature.js
import { useState } from "react";

export function useNewFeature() {
  const [state, setState] = useState(null);
  // logic here
  return { state, setState };
}
```

### 3. Tambah Service

```javascript
// src/services/newService.js
export const newService = {
  getData() {
    // fetch data
  },
};
```

### 4. Gunakan di View

```jsx
// src/views/MainView.jsx
import { useNewFeature } from "../hooks/useNewFeature";
import { NewComponent } from "../components/NewComponent";

export function MainView() {
  const { state } = useNewFeature();
  return <NewComponent data={state} />;
}
```

## 🔧 Best Practices

1. **Components** harus pure dan stateless jika memungkinkan
2. **Hooks** untuk semua business logic yang kompleks
3. **Services** untuk semua external communications
4. **Constants** untuk semua data statis
5. **Views** sebagai orchestrator, bukan implementor

## 📚 Resources

- [React Hooks Documentation](https://react.dev/reference/react)
- [Component Best Practices](https://react.dev/learn/thinking-in-react)
- [Project Structure Guide](https://react.dev/learn/thinking-in-react)
