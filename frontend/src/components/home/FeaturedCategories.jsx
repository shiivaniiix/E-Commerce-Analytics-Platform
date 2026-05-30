const categories = [
  { title: 'Electronics', image: 'https://images.unsplash.com/photo-1510552776732-03e61cf4b144?auto=format&fit=crop&w=800&q=80' },
  { title: 'Fashion', image: 'https://images.unsplash.com/photo-1521335629791-ce4aec67ddc7?auto=format&fit=crop&w=800&q=80' },
  { title: 'Shoes', image: 'https://images.unsplash.com/photo-1519741496360-f1ab487d6236?auto=format&fit=crop&w=800&q=80' },
  { title: 'Accessories', image: 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80' },
  { title: 'Beauty', image: 'https://images.unsplash.com/photo-1500336624523-d727130c3328?auto=format&fit=crop&w=800&q=80' },
  { title: 'Home', image: 'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=800&q=80' },
];

function FeaturedCategories() {
  return (
    <section>
      <div className="mb-8 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Trending categories</p>
          <h2 className="text-3xl font-bold text-slate-900">Shop by category</h2>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categories.map((category) => (
          <article key={category.title} className="group overflow-hidden rounded-[2rem] bg-white shadow-xl transition hover:-translate-y-1 hover:shadow-2xl">
            <div className="relative h-72 overflow-hidden">
              <img src={category.image} alt={category.title} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent" />
              <div className="absolute bottom-6 left-6 text-white">
                <p className="text-2xl font-semibold">{category.title}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default FeaturedCategories;
