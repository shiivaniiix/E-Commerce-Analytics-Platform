import { useEffect, useMemo, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import ProductCard from '../components/product/ProductCard';
import ErrorAlert from '../components/common/ErrorAlert';
import { productService, categoryService } from '../services';
import { normalizeProduct, getErrorMessage } from '../utils/helpers';

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

function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const categoryId = searchParams.get('category');
  const urlSearch = searchParams.get('search') || '';

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState(urlSearch);
  const [sort, setSort] = useState('popular');

  // Load categories once (for the filter label/chips).
  useEffect(() => {
    categoryService.getAll().then(setCategories).catch(() => setCategories([]));
  }, []);

  // Keep the local search box in sync if the URL changes (e.g. from navbar).
  useEffect(() => {
    setQuery(urlSearch);
  }, [urlSearch]);

  // Fetch products whenever the category or search term changes.
  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await productService.getAll({
          categoryId: categoryId || undefined,
          search: urlSearch || undefined,
          pageSize: 100,
        });
        if (!active) return;
        setProducts((data.products || []).map(normalizeProduct));
      } catch (err) {
        if (active) setError(getErrorMessage(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [categoryId, urlSearch]);

  const activeCategory = useMemo(
    () => categories.find((c) => String(c.category_id) === String(categoryId)),
    [categories, categoryId],
  );

  const sorted = useMemo(() => {
    const list = products.slice();
    if (sort === 'price_asc') list.sort((a, b) => a.price - b.price);
    if (sort === 'price_desc') list.sort((a, b) => b.price - a.price);
    if (sort === 'name') list.sort((a, b) => a.name.localeCompare(b.name));
    return list;
  }, [products, sort]);

  const submitSearch = (e) => {
    e.preventDefault();
    const next = new URLSearchParams(searchParams);
    if (query.trim()) next.set('search', query.trim());
    else next.delete('search');
    setSearchParams(next);
  };

  const clearFilters = () => {
    setQuery('');
    setSort('popular');
    setSearchParams({});
  };

  const hasFilters = Boolean(categoryId || urlSearch);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Catalog</p>
          <h1 className="text-3xl font-bold text-slate-900">
            {activeCategory ? activeCategory.category_name : 'All Products'}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {loading ? 'Loading products…' : `${sorted.length} product${sorted.length === 1 ? '' : 's'} found`}
            {urlSearch && ` for “${urlSearch}”`}
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <form onSubmit={submitSearch} className="flex items-center gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products"
              className="w-56 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
            <button
              type="submit"
              className="rounded-full bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Search
            </button>
          </form>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            <option value="popular">Most popular</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="name">Name: A–Z</option>
          </select>
        </div>
      </div>

      {/* Category chips */}
      {categories.length > 0 && (
        <div className="mb-8 flex flex-wrap gap-2">
          <button
            onClick={() => {
              const next = new URLSearchParams(searchParams);
              next.delete('category');
              setSearchParams(next);
            }}
            className={`rounded-full px-4 py-2 text-sm font-medium transition ${
              !categoryId ? 'bg-primary text-white' : 'bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50'
            }`}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.category_id}
              onClick={() => {
                const next = new URLSearchParams(searchParams);
                next.set('category', c.category_id);
                setSearchParams(next);
              }}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                String(categoryId) === String(c.category_id)
                  ? 'bg-primary text-white'
                  : 'bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50'
              }`}
            >
              {c.category_name}
            </button>
          ))}
        </div>
      )}

      {error && <ErrorAlert message={error} />}

      {loading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <ProductSkeleton key={i} />
          ))}
        </div>
      ) : sorted.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-16 text-center">
          <h3 className="text-lg font-semibold text-slate-900">No products found</h3>
          <p className="mt-2 text-sm text-slate-500">
            {hasFilters ? 'Try removing some filters or searching for something else.' : 'Check back soon for new arrivals.'}
          </p>
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="mt-6 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {sorted.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}

export default ProductsPage;
