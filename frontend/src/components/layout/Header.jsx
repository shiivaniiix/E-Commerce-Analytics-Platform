import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-white shadow-md">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-primary">
            ShopHub
          </Link>
          <ul className="flex space-x-6">
            <li><Link to="/" className="text-gray-700 hover:text-primary">Home</Link></li>
            <li><Link to="/products" className="text-gray-700 hover:text-primary">Products</Link></li>
            <li><Link to="/cart" className="text-gray-700 hover:text-primary">Cart</Link></li>
            <li><Link to="/login" className="text-gray-700 hover:text-primary">Login</Link></li>
            <li><Link to="/signup" className="text-gray-700 hover:text-primary">Sign Up</Link></li>
          </ul>
        </div>
      </nav>
    </header>
  );
}

export default Header;
