import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCart, getCartTotal, updateQty, removeFromCart } from '../utils/cart';
import { formatCurrency, PLACEHOLDER_IMAGE } from '../utils/helpers';

function CartPage() {
  const navigate = useNavigate();
  const [cart, setCart] = useState(getCart());

  useEffect(() => {
    const sync = () => setCart(getCart());
    window.addEventListener('cart:updated', sync);
    return () => window.removeEventListener('cart:updated', sync);
  }, []);

  const total = getCartTotal();

  if (!cart.length) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold text-slate-900">Your cart is empty</h1>
        <p className="mt-2 text-slate-500">Browse the catalog and add items you love.</p>
        <Link
          to="/products"
          className="mt-6 inline-flex rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Continue shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold text-slate-900">Shopping Cart</h1>
      <div className="space-y-4">
        {cart.map((it) => (
          <div key={it.id} className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4">
            <img
              src={it.image || PLACEHOLDER_IMAGE}
              alt={it.name}
              onError={(e) => {
                e.currentTarget.src = PLACEHOLDER_IMAGE;
              }}
              className="h-20 w-20 flex-none rounded-xl object-cover"
            />
            <div className="min-w-0 flex-1">
              <Link to={`/products/${it.id}`} className="font-semibold text-slate-900 hover:underline">
                {it.name}
              </Link>
              <p className="text-sm text-slate-500">{formatCurrency(it.price)} each</p>
              <div className="mt-2 flex items-center gap-2">
                <button
                  onClick={() => updateQty(it.id, it.qty - 1)}
                  className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-300 text-slate-700 hover:bg-slate-50"
                  aria-label="Decrease quantity"
                >
                  −
                </button>
                <span className="w-8 text-center text-sm font-medium">{it.qty}</span>
                <button
                  onClick={() => updateQty(it.id, it.qty + 1)}
                  className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-300 text-slate-700 hover:bg-slate-50"
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <span className="font-semibold text-slate-900">{formatCurrency(it.price * it.qty)}</span>
              <button onClick={() => removeFromCart(it.id)} className="text-sm font-medium text-red-600 hover:underline">
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-6">
        <div className="text-lg font-semibold text-slate-900">Total: {formatCurrency(total)}</div>
        <button
          onClick={() => navigate('/purchase')}
          className="rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/20 transition hover:bg-sky-600"
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
}

export default CartPage;
