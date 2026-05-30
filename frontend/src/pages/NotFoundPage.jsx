import { Link } from 'react-router-dom';

function NotFoundPage() {
  return (
    <div className="text-center py-12">
      <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="text-gray-600 mb-6">Sorry, the page you're looking for doesn't exist.</p>
      <Link to="/" className="btn-primary">Go Home</Link>
    </div>
  );
}

export default NotFoundPage;
