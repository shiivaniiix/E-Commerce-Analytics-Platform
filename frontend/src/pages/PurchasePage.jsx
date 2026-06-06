import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCart, getCartTotal, clearCart } from '../utils/cart';
import { formatCurrency, PLACEHOLDER_IMAGE } from '../utils/helpers';
import { useToast } from '../contexts/ToastContext';

function PurchasePage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [processing, setProcessing] = useState(false);

  const cart = getCart();
  const total = getCartTotal();

  const handleCheckout = async () => {
    setProcessing(true);
    try {
      // Demo checkout: simulate processing, then clear cart and confirm.
      await new Promise((r) => setTimeout(r, 900));
      clearCart();
      navigate('/purchase/success');
    } catch (e) {
      toast.error('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (!cart.length) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold text-slate-900">Your cart is empty</h1>
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
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold text-slate-900">Checkout</h1>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-4">
          {cart.map((it) => (
            <div key={it.id} className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4">
              <img
                src={it.image || PLACEHOLDER_IMAGE}
                alt={it.name}
                onError={(e) => {
                  e.currentTarget.src = PLACEHOLDER_IMAGE;
                }}
                className="h-20 w-20 rounded-xl object-cover"
              />
              <div>
                <div className="font-semibold text-slate-900">{it.name}</div>
                <div className="text-sm text-slate-500">Qty: {it.qty}</div>
              </div>
              <div className="ml-auto font-semibold text-slate-900">{formatCurrency(it.price * it.qty)}</div>
            </div>
          ))}
        </div>

        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-6">
          <div className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-400">Order summary</div>
          <div className="mb-6 flex items-center justify-between text-lg font-semibold text-slate-900">
            <span>Total</span>
            <span>{formatCurrency(total)}</span>
          </div>
          <button
            onClick={handleCheckout}
            disabled={processing}
            className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/20 transition hover:bg-sky-600 disabled:opacity-50"
          >
            {processing ? 'Processing…' : 'Place Order'}
          </button>
        </aside>
      </div>
    </div>
  );
}

export default PurchasePage;
