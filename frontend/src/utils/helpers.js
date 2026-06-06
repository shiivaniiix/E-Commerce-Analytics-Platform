export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const getErrorMessage = (error) => {
  if (!error) return 'An error occurred';
  // Axios error
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg || d).join(', ');
    return detail;
  }
  if (error.response?.data?.message) return error.response.data.message;
  // Plain object thrown by services ({ detail } or { message })
  if (error.detail) {
    if (Array.isArray(error.detail)) return error.detail.map((d) => d.msg || d).join(', ');
    return error.detail;
  }
  if (error.message) return error.message;
  return 'An error occurred';
};

// Neutral placeholder used when a product has no image.
export const PLACEHOLDER_IMAGE =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600"><rect width="100%" height="100%" fill="#f1f5f9"/><text x="50%" y="50%" font-family="sans-serif" font-size="28" fill="#94a3b8" text-anchor="middle" dominant-baseline="middle">No image</text></svg>`,
  );

// Map a backend product (product_name, selling_price, product_id, ...) to the
// flat shape the UI components consume.
export const normalizeProduct = (p) => {
  if (!p) return null;
  return {
    id: p.product_id,
    name: p.product_name,
    price: Number(p.selling_price),
    brand: p.brand || null,
    description: p.description || '',
    image: p.image_url || PLACEHOLDER_IMAGE,
    stock: p.stock_quantity ?? 0,
    categoryId: p.category_id,
    categoryName: p.category?.category_name || null,
  };
};
