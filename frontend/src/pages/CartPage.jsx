import { useNavigate } from 'react-router-dom';

function CartPage() {
  const navigate = useNavigate();
  const cart = (() => {
    try {
      return JSON.parse(localStorage.getItem('cart') || '[]');
    } catch (e) {
      return [];
    }
  })();

  const total = cart.reduce((s, it) => s + it.price * it.qty, 0);

  if (!cart.length) return <div className="text-center py-12">Your cart is empty.</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Shopping Cart</h1>
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

      <div className="mt-6 flex items-center justify-between">
        <div className="text-lg font-semibold">Total: ${total.toFixed(2)}</div>
        <button onClick={() => navigate('/purchase')} className="rounded-md bg-green-600 px-4 py-2 text-white">Proceed to Checkout</button>
      </div>
    </div>
  );
}

export default CartPage;
