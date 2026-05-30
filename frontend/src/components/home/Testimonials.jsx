const testimonials = [
  { title: 'Fast delivery', description: 'Premium shipping in 2 days. Quality packaging and reliable tracking.', author: 'Olivia R.' },
  { title: 'Secure checkout', description: 'I love the smooth payment flow and easy order tracking.', author: 'Jason T.' },
  { title: 'Hassle-free returns', description: 'Returned a product without any stress. Excellent support.', author: 'Mia K.' },
];

function Testimonials() {
  return (
    <section>
      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Trusted by shoppers</p>
          <h2 className="text-3xl font-bold text-slate-900">Shop with confidence</h2>
        </div>
        <div className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm text-slate-700 shadow-sm">
          120k+ happy customers
        </div>
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        {testimonials.map((item) => (
          <div key={item.author} className="space-y-4 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-lg">
            <p className="text-lg font-semibold text-slate-900">{item.title}</p>
            <p className="text-slate-600">{item.description}</p>
            <p className="text-sm font-semibold text-slate-900">{item.author}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Testimonials;
