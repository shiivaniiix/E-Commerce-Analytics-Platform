import { Link, NavLink } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

function Navbar() {
  const [open, setOpen] = useState(false);

  const auth = useAuth();

  const handleLogout = () => {
    auth.logout();
  };

  const cartCount = (() => {
    try {
      const cart = JSON.parse(localStorage.getItem('cart') || '[]');
      return Array.isArray(cart) ? cart.length : 0;
    } catch (e) {
      return 0;
    }
  })();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3 text-xl font-black tracking-tight text-slate-900">
          <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-white shadow-lg shadow-primary/20">S</span>
          ShopHub
        </Link>

        <button
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          Menu
        </button>

        <div className={`absolute inset-x-0 top-full bg-white shadow-xl md:static md:block md:shadow-none ${open ? 'block' : 'hidden'}`}>
          <div className="flex flex-col gap-4 px-4 py-5 md:flex-row md:items-center md:gap-6 md:px-0 md:py-0">
            <NavLink to="/products" className={({ isActive }) => `rounded-full px-4 py-2 text-sm font-medium transition ${isActive ? 'bg-primary text-white' : 'text-slate-700 hover:bg-slate-100'}`}>
              Products
            </NavLink>
            {auth.isAuthenticated ? (
              <>
                <NavLink to="/profile" className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
                  Profile
                </NavLink>
                <NavLink to="/cart" className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
                  Cart
                </NavLink>
                <button onClick={handleLogout} className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
                  Logout
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
                  Login
                </NavLink>
                <NavLink to="/signup" className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800">
                  Sign Up
                </NavLink>
              </>
            )}
          </div>
        </div>

          <div className="hidden items-center gap-4 md:flex">
          <div className="relative hidden md:block">
            <input
              type="search"
              placeholder="Search products"
              className="w-72 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <Link to="/cart" className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
            <span>Cart</span>
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-sm text-slate-900">{cartCount}</span>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
