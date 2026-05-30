import { useEffect, useState } from 'react';
import { healthCheckService } from '../../services';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

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
    <div className="space-y-8">
      {error && <ErrorAlert message={error} />}
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to ShopHub</h1>
        <p className="text-xl text-gray-600">Your premium e-commerce destination</p>
      </div>

      {health && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-green-800">✓ Backend Connected</h2>
          <p className="text-green-700 mt-2">Status: {health.status}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="card">
          <h3 className="text-xl font-semibold mb-2">Wide Selection</h3>
          <p className="text-gray-600">Browse thousands of products from top brands</p>
        </div>
        <div className="card">
          <h3 className="text-xl font-semibold mb-2">Fast Shipping</h3>
          <p className="text-gray-600">Quick and reliable delivery to your doorstep</p>
        </div>
        <div className="card">
          <h3 className="text-xl font-semibold mb-2">Secure Payment</h3>
          <p className="text-gray-600">Safe and secure payment processing</p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
