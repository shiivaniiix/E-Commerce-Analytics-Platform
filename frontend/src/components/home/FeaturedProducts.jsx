import ProductCard from '../product/ProductCard';

const products = [
  { id: 1, name: 'Aero Runner Sneakers', price: 129, oldPrice: 179, rating: 4.8, image: 'https://images.unsplash.com/photo-1519741496360-f1ab487d6236?auto=format&fit=crop&w=800&q=80' },
  { id: 2, name: 'Urban Tech Backpack', price: 89, oldPrice: 129, rating: 4.7, image: 'https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=800&q=80' },
  { id: 3, name: 'Luxe Sunglasses', price: 59, oldPrice: 89, rating: 4.9, image: 'https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=800&q=80' },
  { id: 4, name: 'Signature Watch', price: 249, oldPrice: 325, rating: 4.6, image: 'https://images.unsplash.com/photo-1519648023493-d82b5f8d7a7c?auto=format&fit=crop&w=800&q=80' },
];

function FeaturedProducts() {
  return (
    <section>
      <div className="mb-8 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Featured collection</p>
          <h2 className="text-3xl font-bold text-slate-900">Premium picks for you</h2>
        </div>
        <button className="rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800">
          View all products
        </button>
      </div>
      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}

export default FeaturedProducts;
