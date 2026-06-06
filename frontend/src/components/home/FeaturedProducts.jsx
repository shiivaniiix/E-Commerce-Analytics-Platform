import { useNavigate } from 'react-router-dom';
import ProductCard from '../product/ProductCard';

function ProductSkeleton() {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white">
      <div className="aspect-square animate-pulse bg-slate-200" />
      <div className="space-y-3 p-5">
        <div className="h-3 w-1/3 animate-pulse rounded bg-slate-200" />
        <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200" />
        <div className="h-6 w-1/2 animate-pulse rounded bg-slate-200" />
      </div>
    </div>
  );
}

function FeaturedProducts({ products = [], loading = false }) {
  const navigate = useNavigate();

  return (
    <section>
      <div className="mb-8 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Featured collection</p>
          <h2 className="text-3xl font-bold text-slate-900">Premium picks for you</h2>
        </div>
        <button
          onClick={() => navigate('/products')}
          className="rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          View all products
        </button>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => <ProductSkeleton key={i} />)
          : products.map((product) => <ProductCard key={product.id} product={product} />)}
      </div>
    </section>
  );
}

export default FeaturedProducts;
