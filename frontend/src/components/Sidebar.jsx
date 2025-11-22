export function Sidebar({ isOpen, onClose }) {
  const menuItems = [
    {
      label: "Beranda",
      onClick: () => window.scrollTo({ top: 0, behavior: "smooth" }),
    },
    {
      label: "Riwayat",
      onClick: () =>
        document.querySelector("#root")?.scrollIntoView({ behavior: "smooth" }),
    },
  ];

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black transition-opacity duration-300 ${
          isOpen ? "opacity-40" : "opacity-0"
        }`}
        style={{ pointerEvents: isOpen ? "auto" : "none" }}
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside
        className={`absolute left-0 top-0 h-full w-72 bg-white p-6 shadow-lg transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{ pointerEvents: isOpen ? "auto" : "none" }}
      >
        <h4 className="font-semibold text-lg mb-4">Menu</h4>
        <ul className="space-y-3">
          {menuItems.map((item, idx) => (
            <li key={idx}>
              <button
                className="w-full text-left transition transform active:scale-95 hover:bg-gray-50 rounded-md px-2 py-1"
                onClick={() => {
                  item.onClick();
                  onClose();
                }}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
