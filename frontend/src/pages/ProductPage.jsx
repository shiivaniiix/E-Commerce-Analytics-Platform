import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [qty, setQty] = useState(1);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/products/${id}`);
        if (!res.ok) throw new Error('Product not found');
        const data = await res.json();
        setProduct(data);
      } catch (err) {
        // Fallback - simple sample product when API not available
        setProduct({
          id,
          name: `Sample Product ${id}`,
          description: 'This is a sample product description. Replace with backend data.',
          price: 99.0,
          images: [
            'https://images.unsplash.com/photo-1519741496360-f1ab487d6236?auto=format&fit=crop&w=1200&q=80',
            'https://images.unsplash.com/photo-1520975915481-7e8f28f6a2f4?auto=format&fit=crop&w=1200&q=80'
          ],
          reviews: [{ id: 1, author: 'Sam', rating: 5, text: 'Love it!' }],
          stock: 12,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id]);

  const addToCart = () => {
    try {
      const raw = localStorage.getItem('cart') || '[]';
      const cart = JSON.parse(raw);
      const existing = cart.find((c) => c.id === product.id);
      if (existing) existing.qty += Number(qty);
      else cart.push({ id: product.id, name: product.name, price: product.price, qty: Number(qty), image: product.images?.[0] });
      localStorage.setItem('cart', JSON.stringify(cart));
      // stay on page
      // simple feedback
      // eslint-disable-next-line no-alert
      alert('Added to cart');
    } catch (e) {
      // ignore
    }
  };

  const buyNow = () => {
    addToCart();
    navigate('/purchase');
  };

  if (loading) return <div>Loading product...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div>
        <div className="space-y-4">
          <div className="rounded-xl overflow-hidden">
            <img src={product.images?.[0]} alt={product.name} className="w-full object-cover" />
          </div>
          <div className="grid grid-cols-4 gap-2">
            {(product.images || []).map((img, i) => (
              <img key={i} src={img} alt={`${product.name}-${i}`} className="h-20 w-full rounded-md object-cover" />
            ))}
          </div>
        </div>
      </div>

      <div>
        <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
        <p className="text-slate-600 mb-4">{product.description}</p>
        <div className="mb-4">
          <span className="text-2xl font-bold">${product.price}</span>
          <span className="ml-3 text-sm text-slate-500">{product.stock > 0 ? 'In stock' : 'Out of stock'}</span>
        </div>

        <div className="mb-4 flex items-center gap-4">
          <label className="text-sm">Quantity</label>
          <input type="number" min="1" value={qty} onChange={(e) => setQty(e.target.value)} className="w-20 rounded-md border px-3 py-2" />
        </div>

        <div className="flex gap-3">
          <button onClick={addToCart} className="rounded-md bg-blue-600 px-4 py-2 text-white">Add to cart</button>
          <button onClick={buyNow} className="rounded-md border border-blue-600 px-4 py-2 text-blue-600">Buy now</button>
        </div>

        <div className="mt-8">
          <h3 className="text-xl font-semibold">Reviews</h3>
          <div className="mt-4 space-y-4">
            {(product.reviews || []).map((r) => (
              <div key={r.id} className="rounded-md border p-4">
                <div className="flex items-center justify-between">
                  <strong>{r.author}</strong>
                  <span>{r.rating} ★</span>
                </div>
                <p className="text-slate-600">{r.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductPage;
