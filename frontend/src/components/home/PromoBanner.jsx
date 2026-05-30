import { Button } from '../common';

function PromoBanner() {
  return (
    <section className="rounded-[2rem] bg-slate-950 px-8 py-12 text-white shadow-2xl shadow-slate-950/20">
      <div className="grid gap-8 lg:grid-cols-[1.4fr_1fr] lg:items-center">
        <div className="space-y-4">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Mid-season sale</p>
          <h3 className="text-4xl font-black tracking-tight sm:text-5xl">Up to 40% off top-rated styles.</h3>
          <p className="max-w-xl text-lg text-slate-300">Refresh your wardrobe with premium essentials, limited editions, and fast shipping across the country.</p>
          <Button variant="secondary">Shop the sale</Button>
        </div>
        <div className="rounded-[2rem] bg-slate-900/50 p-6">
          <div className="space-y-4">
            <div className="rounded-3xl bg-slate-800 p-5 shadow-xl shadow-black/20">
              <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Limited Offer</p>
              <p className="text-3xl font-bold text-white">Free shipping over $75</p>
            </div>
            <div className="rounded-3xl bg-slate-800 p-5 shadow-xl shadow-black/15">
              <p className="text-base text-slate-400">Easy returns within 30 days</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default PromoBanner;
