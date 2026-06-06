import { useNavigate } from 'react-router-dom';
import { Button } from '../common';
import { formatCurrency, PLACEHOLDER_IMAGE } from '../../utils/helpers';
import { addToCart } from '../../utils/cart';
import { useToast } from '../../contexts/ToastContext';

// `product` is the normalized shape: { id, name, price, brand, image, stock, categoryName }
function ProductCard({ product }) {
  const navigate = useNavigate();
  const toast = useToast();

  const goToDetail = () => navigate(`/products/${product.id}`);

  const handleAdd = (e) => {
    e.stopPropagation();
    if (product.stock <= 0) {
      toast.error('This product is out of stock.');
      return;
    }
    addToCart(product, 1);
    toast.success(`${product.name} added to cart`);
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      goToDetail();
    }
  };

  return (
    <article
      role="link"
      tabIndex={0}
      onClick={goToDetail}
      onKeyDown={onKeyDown}
      className="group flex cursor-pointer flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:border-slate-300 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-primary/40"
    >
      <div className="relative aspect-square overflow-hidden bg-slate-100">
        <img
          src={product.image || PLACEHOLDER_IMAGE}
          alt={product.name}
          loading="lazy"
          onError={(e) => {
            e.currentTarget.src = PLACEHOLDER_IMAGE;
          }}
          className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
        />
        {product.stock <= 0 && (
          <span className="absolute left-3 top-3 rounded-full bg-slate-900/80 px-3 py-1 text-xs font-semibold text-white">
            Out of stock
          </span>
        )}
        {product.categoryName && (
          <span className="absolute right-3 top-3 rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-slate-600 shadow-sm">
            {product.categoryName}
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="space-y-1">
          {product.brand && (
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{product.brand}</p>
          )}
          <h3 className="line-clamp-2 text-base font-semibold text-slate-900">{product.name}</h3>
        </div>
        <div className="mt-auto flex items-center justify-between gap-3 pt-2">
          <p className="text-lg font-bold text-slate-900">{formatCurrency(product.price)}</p>
          <Button variant="primary" className="px-4 py-2 text-xs" onClick={handleAdd}>
            Add to cart
          </Button>
        </div>
      </div>
    </article>
  );
}

export default ProductCard;
