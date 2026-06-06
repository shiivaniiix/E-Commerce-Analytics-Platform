import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { productService } from '../services';
import { normalizeProduct, formatCurrency, getErrorMessage, PLACEHOLDER_IMAGE } from '../utils/helpers';
import { addToCart } from '../utils/cart';
import { useToast } from '../contexts/ToastContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

function ProductPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState(null);
  const [qty, setQty] = useState(1);

  useEffect(() => {
    let active = true;
    const fetchProduct = async () => {
      setLoading(true);
      setError(null);
      setNotFound(false);
      try {
        const data = await productService.getById(productId);
        if (!active) return;
        setProduct(normalizeProduct(data));
      } catch (err) {
        if (!active) return;
        if (err.response?.status === 404) {
          setNotFound(true);
        } else {
          setError(getErrorMessage(err));
        }
      } finally {
        if (active) setLoading(false);
      }
    };
    fetchProduct();
    return () => {
      active = false;
    };
  }, [productId]);

  const handleAddToCart = () => {
    if (!product) return;
    if (product.stock <= 0) {
      toast.error('This product is out of stock.');
      return;
    }
    addToCart(product, qty);
    toast.success(`Added ${qty} × ${product.name} to cart`);
  };

  const handleBuyNow = () => {
    if (!product || product.stock <= 0) {
      toast.error('This product is out of stock.');
      return;
    }
    addToCart(product, qty);
    navigate('/purchase');
  };

  if (loading) return <LoadingSpinner />;

  if (notFound) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold text-slate-900">Product not found</h1>
        <p className="mt-2 text-slate-500">The product you’re looking for doesn’t exist or is no longer available.</p>
        <Link
          to="/products"
          className="mt-6 inline-flex rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Back to products
        </Link>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold text-slate-900">Something went wrong</h1>
        <p className="mt-2 text-red-600">{error}</p>
        <button
          onClick={() => navigate(0)}
          className="mt-6 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Try again
        </button>
      </div>
    );
  }

  const inStock = product.stock > 0;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <nav className="mb-6 text-sm text-slate-500">
        <Link to="/products" className="hover:text-slate-900">Products</Link>
        {product.categoryName && (
          <>
            <span className="mx-2">/</span>
            <Link to={`/products?category=${product.categoryId}`} className="hover:text-slate-900">
              {product.categoryName}
            </Link>
          </>
        )}
        <span className="mx-2">/</span>
        <span className="text-slate-700">{product.name}</span>
      </nav>

      <div className="grid gap-10 lg:grid-cols-2">
        <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-100">
          <img
            src={product.image || PLACEHOLDER_IMAGE}
            alt={product.name}
            onError={(e) => {
              e.currentTarget.src = PLACEHOLDER_IMAGE;
            }}
            className="aspect-square w-full object-cover"
          />
        </div>

        <div className="flex flex-col">
          {product.categoryName && (
            <span className="mb-3 inline-flex w-fit rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              {product.categoryName}
            </span>
          )}
          <h1 className="text-3xl font-bold text-slate-900">{product.name}</h1>
          {product.brand && <p className="mt-1 text-sm text-slate-500">by {product.brand}</p>}

          <div className="mt-5 flex items-center gap-4">
            <span className="text-3xl font-bold text-slate-900">{formatCurrency(product.price)}</span>
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${
                inStock ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
              }`}
            >
              {inStock ? `In stock (${product.stock})` : 'Out of stock'}
            </span>
          </div>

          {product.description && (
            <p className="mt-6 leading-relaxed text-slate-600">{product.description}</p>
          )}

          <div className="mt-8 flex items-center gap-4">
            <label htmlFor="qty" className="text-sm font-medium text-slate-700">Quantity</label>
            <input
              id="qty"
              type="number"
              min="1"
              max={inStock ? product.stock : 1}
              value={qty}
              disabled={!inStock}
              onChange={(e) => setQty(Math.max(1, Number(e.target.value) || 1))}
              className="w-20 rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:bg-slate-100"
            />
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={handleAddToCart}
              disabled={!inStock}
              className="rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/20 transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Add to cart
            </button>
            <button
              onClick={handleBuyNow}
              disabled={!inStock}
              className="rounded-full border border-slate-300 px-6 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Buy now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductPage;
