function Button({ children, className = '', variant = 'primary', type = 'button', ...props }) {
  const baseStyles = 'inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary';
  const variants = {
    primary: 'bg-primary text-white shadow-lg shadow-primary/10 hover:bg-sky-600',
    secondary: 'bg-gray-900 text-white hover:bg-gray-800',
    ghost: 'bg-white text-gray-900 border border-gray-200 hover:bg-gray-50',
    danger: 'bg-red-600 text-white hover:bg-red-500',
  };

  return (
    <button type={type} className={`${baseStyles} ${variants[variant] || variants.primary} ${className}`} {...props}>
      {children}
    </button>
  );
}

export default Button;
