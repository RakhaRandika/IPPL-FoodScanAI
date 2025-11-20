export const Button = ({ children, className = "", ...props }) => (
  <button
    {...props}
    className={`px-4 py-2 rounded-lg font-medium transition ${className}`}
  >
    {children}
  </button>
);
