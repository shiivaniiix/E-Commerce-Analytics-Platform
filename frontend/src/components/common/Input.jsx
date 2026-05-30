function Input({ label, error, className = '', ...props }) {
  return (
    <label className="block text-sm font-medium text-gray-700">
      {label && <span className="mb-2 block text-sm font-medium text-slate-700">{label}</span>}
      <input
        className={`w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 shadow-sm transition duration-200 focus:border-primary focus:ring-2 focus:ring-primary/10 ${className}`}
        {...props}
      />
      {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
    </label>
  );
}

export default Input;
