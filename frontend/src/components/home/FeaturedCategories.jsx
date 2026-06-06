import { useNavigate } from 'react-router-dom';

// Curated imagery per known category name; falls back to a gradient tile.
const CATEGORY_IMAGES = {
  electronics: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=800&q=80',
  clothing: 'https://images.unsplash.com/photo-1521335629791-ce4aec67ddc7?auto=format&fit=crop&w=800&q=80',
  fashion: 'https://images.unsplash.com/photo-1521335629791-ce4aec67ddc7?auto=format&fit=crop&w=800&q=80',
  books: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80',
  food: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80',
  'home & garden': 'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=800&q=80',
};

const imageFor = (name) => CATEGORY_IMAGES[(name || '').toLowerCase()] || null;

function FeaturedCategories({ categories = [], loading = false }) {
  const navigate = useNavigate();

  const goToCategory = (category) => {
    navigate(`/products?category=${category.category_id}`);
  };

  return (
    <section>
      <div className="mb-8 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Trending categories</p>
          <h2 className="text-3xl font-bold text-slate-900">Shop by category</h2>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-72 animate-pulse rounded-3xl bg-slate-200" />
          ))}
        </div>
      ) : categories.length === 0 ? (
        <p className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
          No categories available yet.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((category) => {
            const img = imageFor(category.category_name);
            return (
              <button
                key={category.category_id}
                type="button"
                onClick={() => goToCategory(category)}
                className="group relative h-72 overflow-hidden rounded-3xl bg-slate-900 text-left shadow-lg transition duration-200 hover:-translate-y-1 hover:shadow-2xl focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                {img ? (
                  <img
                    src={img}
                    alt={category.category_name}
                    className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
                  />
                ) : (
                  <div className="h-full w-full bg-gradient-to-br from-primary/80 to-secondary/80" />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent" />
                <div className="absolute bottom-6 left-6 right-6 text-white">
                  <p className="text-2xl font-semibold">{category.category_name}</p>
                  <p className="mt-1 text-sm text-white/80 opacity-0 transition group-hover:opacity-100">
                    Shop {category.category_name} →
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default FeaturedCategories;
