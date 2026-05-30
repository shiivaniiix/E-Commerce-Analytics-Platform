import React from 'react';
import { Link } from 'react-router-dom';

function OrderSuccessPage() {
  return (
    <div className="text-center py-12">
      <h1 className="text-3xl font-bold mb-4">Order placed successfully</h1>
      <p className="text-slate-600 mb-6">Thanks for your purchase. Your order is being processed.</p>
      <Link to="/" className="rounded-md bg-slate-900 px-4 py-2 text-white">Return to Shop</Link>
    </div>
  );
}

export default OrderSuccessPage;
