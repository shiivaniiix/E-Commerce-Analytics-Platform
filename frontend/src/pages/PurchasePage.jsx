import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function PurchasePage() {
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);

  const cart = (() => {
    try {
      return JSON.parse(localStorage.getItem('cart') || '[]');
    } catch (e) {
      return [];
    }
  })();

  const total = cart.reduce((s, it) => s + it.price * it.qty, 0);

  const handleCheckout = async () => {
    setProcessing(true);
    try {
      // In a real app, call backend /orders endpoint to create the order using JWT auth.
      // For demo: simulate success, clear cart and redirect to success page.
      await new Promise((r) => setTimeout(r, 900));
      localStorage.removeItem('cart');
      navigate('/purchase/success');
    } catch (e) {
      // eslint-disable-next-line no-alert
      alert('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (!cart.length) return <div className="text-center py-12">Your cart is empty.</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Checkout</h1>
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div>
          <div className="space-y-4">
            {cart.map((it) => (
              <div key={it.id} className="flex items-center gap-4 rounded-md border p-4">
                <img src={it.image} alt={it.name} className="h-20 w-20 rounded-md object-cover" />
                <div>
                  <div className="font-semibold">{it.name}</div>
                  <div className="text-sm text-slate-600">Qty: {it.qty}</div>
                </div>
                <div className="ml-auto font-semibold">${(it.price * it.qty).toFixed(2)}</div>
              </div>
            ))}
          </div>
        </div>

        <aside className="rounded-md border p-6">
          <div className="mb-4 text-sm text-slate-600">Order summary</div>
          <div className="flex items-center justify-between text-lg font-semibold mb-4"> <span>Total</span> <span>${total.toFixed(2)}</span></div>
          <button onClick={handleCheckout} disabled={processing} className="w-full rounded-md bg-green-600 px-4 py-3 text-white">
            {processing ? 'Processing...' : 'Place Order'}
          </button>
        </aside>
      </div>
    </div>
  );
}

export default PurchasePage;
