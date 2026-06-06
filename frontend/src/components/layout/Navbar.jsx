import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { getCartCount } from '../../utils/cart';

function Navbar() {
  const [open, setOpen] = useState(false);
  const [cartCount, setCartCount] = useState(getCartCount());
  const [search, setSearch] = useState('');
  const auth = useAuth();
  const navigate = useNavigate();

  // Keep the cart badge in sync with cart changes (same or other tabs).
  useEffect(() => {
    const update = () => setCartCount(getCartCount());
    window.addEventListener('cart:updated', update);
    window.addEventListener('storage', update);
    return () => {
      window.removeEventListener('cart:updated', update);
      window.removeEventListener('storage', update);
    };
  }, []);

  const handleLogout = () => {
    auth.logout();
    setOpen(false);
  };

  const submitSearch = (e) => {
    e.preventDefault();
    const q = search.trim();
    navigate(q ? `/products?search=${encodeURIComponent(q)}` : '/products');
    setOpen(false);
  };

  const navLinkClass = ({ isActive }) =>
    `rounded-full px-4 py-2 text-sm font-medium transition ${
      isActive ? 'bg-primary text-white' : 'text-slate-700 hover:bg-slate-100'
    }`;

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
          <div className="flex flex-col gap-4 px-4 py-5 md:flex-row md:items-center md:gap-2 md:px-0 md:py-0">
            {auth.isAuthenticated ? (
              <>
                <NavLink to="/products" className={navLinkClass} onClick={() => setOpen(false)}>
                  Products
                </NavLink>
                <NavLink to="/profile" className={navLinkClass} onClick={() => setOpen(false)}>
                  Profile
                </NavLink>
                <NavLink to="/cart" className={navLinkClass} onClick={() => setOpen(false)}>
                  Cart
                </NavLink>
                <button
                  onClick={handleLogout}
                  className="rounded-full px-4 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={navLinkClass} onClick={() => setOpen(false)}>
                  Login
                </NavLink>
                <NavLink to="/signup" className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800" onClick={() => setOpen(false)}>
                  Sign Up
                </NavLink>
              </>
            )}
          </div>
        </div>

        <div className="hidden items-center gap-4 md:flex">
          {auth.isAuthenticated && (
            <>
              <form onSubmit={submitSearch} className="relative hidden md:block">
                <input
                  type="search"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search products"
                  className="w-64 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </form>
              <Link
                to="/cart"
                className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <span>Cart</span>
                <span className="inline-flex h-7 min-w-7 items-center justify-center rounded-full bg-primary px-2 text-xs font-semibold text-white">
                  {cartCount}
                </span>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
