import { useEffect, useState } from 'react';
import { healthCheckService } from '../services';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import {
  HeroSection,
  FeaturedCategories,
  FeaturedProducts,
  PromoBanner,
  Testimonials,
} from '../components/home';

function HomePage() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await healthCheckService.check();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError('Failed to connect to backend');
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <main className="space-y-12">
      {error && <ErrorAlert message={error} />}
      <HeroSection />
      <FeaturedCategories />
      <FeaturedProducts />
      <PromoBanner />
      <Testimonials />

      {health && (
        <section className="rounded-[1.75rem] border border-slate-200 bg-white p-8 shadow-lg">
          <h2 className="text-xl font-semibold text-slate-900">Backend connection verified</h2>
          <p className="mt-2 text-slate-600">Status: {health.status}</p>
        </section>
      )}
    </main>
  );
}

export default HomePage;
