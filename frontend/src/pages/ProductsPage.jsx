import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/product/ProductCard';

const SAMPLE_PRODUCTS = Array.from({ length: 12 }).map((_, i) => ({
  id: i + 1,
  name: `Product ${i + 1}`,
  price: Math.round(20 + Math.random() * 200),
  rating: (4 + Math.random()).toFixed(1),
  image: 'https://images.unsplash.com/photo-1519741496360-f1ab487d6236?auto=format&fit=crop&w=800&q=80',
}));

function ProductsPage() {
  const [query, setQuery] = useState('');
  const [sort, setSort] = useState('popular');

  const filtered = useMemo(() => {
    let list = SAMPLE_PRODUCTS.slice();
    if (query) list = list.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()));
    if (sort === 'price_asc') list.sort((a, b) => a.price - b.price);
    if (sort === 'price_desc') list.sort((a, b) => b.price - a.price);
    return list;
  }, [query, sort]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Products</h1>
          <p className="text-sm text-slate-500">Browse our catalog</p>
        </div>
        <div className="flex items-center gap-3">
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search products" className="rounded-md border px-3 py-2" />
          <select value={sort} onChange={(e) => setSort(e.target.value)} className="rounded-md border px-3 py-2">
            <option value="popular">Most popular</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
          </select>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((p) => (
          <Link key={p.id} to={`/product/${p.id}`}>
            <ProductCard product={p} />
          </Link>
        ))}
      </div>
    </div>
  );
}

export default ProductsPage;
