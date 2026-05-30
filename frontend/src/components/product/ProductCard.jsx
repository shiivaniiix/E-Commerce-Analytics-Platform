import { Button } from '../common';

function ProductCard({ product }) {
  return (
    <article className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
      <div className="relative h-72 overflow-hidden bg-slate-100">
        <img
          src={product.image}
          alt={product.name}
          className="h-full w-full object-cover transition duration-500 hover:scale-105"
        />
      </div>
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold text-slate-900">{product.name}</h3>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">{product.rating} ★</span>
        </div>
        <div className="space-y-2">
          <p className="text-sm text-slate-500">{product.description ?? 'A curated essential with premium materials and style.'}</p>
          <div className="flex items-center gap-3">
            <p className="text-xl font-bold text-slate-900">${product.price}</p>
            {product.oldPrice && <p className="text-sm text-slate-500 line-through">${product.oldPrice}</p>}
          </div>
        </div>
        <Button className="w-full" variant="primary">Add to cart</Button>
      </div>
    </article>
  );
}

export default ProductCard;
