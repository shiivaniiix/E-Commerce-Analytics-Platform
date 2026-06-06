// Centralized cart helper backed by localStorage.
// Item shape: { id, name, price, qty, image }
// Dispatches a 'cart:updated' event so UI (e.g. the navbar badge) can react.

const CART_KEY = 'cart';

const read = () => {
  try {
    const raw = localStorage.getItem(CART_KEY) || '[]';
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const write = (cart) => {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  window.dispatchEvent(new Event('cart:updated'));
};

export const getCart = () => read();

export const getCartCount = () =>
  read().reduce((sum, item) => sum + (Number(item.qty) || 0), 0);

export const getCartTotal = () =>
  read().reduce((sum, item) => sum + Number(item.price) * Number(item.qty), 0);

export const addToCart = (product, qty = 1) => {
  const cart = read();
  const id = product.id;
  const existing = cart.find((c) => c.id === id);
  if (existing) {
    existing.qty += Number(qty);
  } else {
    cart.push({
      id,
      name: product.name,
      price: Number(product.price),
      qty: Number(qty),
      image: product.image || null,
    });
  }
  write(cart);
  return cart;
};

export const updateQty = (id, qty) => {
  const cart = read();
  const item = cart.find((c) => c.id === id);
  if (item) {
    item.qty = Math.max(1, Number(qty));
    write(cart);
  }
  return cart;
};

export const removeFromCart = (id) => {
  const cart = read().filter((c) => c.id !== id);
  write(cart);
  return cart;
};

export const clearCart = () => {
  write([]);
  return [];
};
