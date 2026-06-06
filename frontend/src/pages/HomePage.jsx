import { useEffect, useState } from 'react';
import { categoryService, productService } from '../services';
import { normalizeProduct, getErrorMessage } from '../utils/helpers';
import ErrorAlert from '../components/common/ErrorAlert';
import {
  HeroSection,
  FeaturedCategories,
  FeaturedProducts,
  PromoBanner,
  Testimonials,
} from '../components/home';

function HomePage() {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [cats, productData] = await Promise.all([
          categoryService.getAll(),
          productService.getAll({ pageSize: 8 }),
        ]);
        if (!active) return;
        setCategories(cats || []);
        setProducts((productData.products || []).map(normalizeProduct));
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
  }, []);

  return (
    <main className="mx-auto max-w-7xl space-y-16 px-4 py-10 sm:px-6 lg:px-8">
      {error && <ErrorAlert message={`Could not load store data: ${error}`} />}
      <HeroSection />
      <FeaturedCategories categories={categories} loading={loading} />
      <FeaturedProducts products={products.slice(0, 4)} loading={loading} />
      <PromoBanner />
      <Testimonials />
    </main>
  );
}

export default HomePage;
