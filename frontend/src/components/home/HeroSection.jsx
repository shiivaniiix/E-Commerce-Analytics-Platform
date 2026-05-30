import { Button } from '../common';

function HeroSection() {
  return (
    <section className="overflow-hidden rounded-[2rem] bg-gradient-to-r from-slate-950 via-slate-900 to-slate-700 px-6 py-16 text-white sm:px-10 lg:px-16">
      <div className="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="space-y-6">
          <span className="inline-flex rounded-full bg-white/10 px-4 py-2 text-sm font-semibold uppercase tracking-[0.24em] text-slate-100">Spring Drop</span>
          <h1 className="max-w-2xl text-5xl font-black tracking-tight sm:text-6xl">
            Discover premium streetwear and performance gear for every day.
          </h1>
          <p className="max-w-xl text-lg text-slate-200 sm:text-xl">
            Shop the latest curated collection with fast checkout, free shipping, and trusted customer care.
          </p>
          <div className="flex flex-wrap gap-4">
            <Button variant="primary">Shop New Arrivals</Button>
            <Button variant="ghost" className="border-white/20 text-white hover:bg-white/10">Explore Collections</Button>
          </div>
        </div>

        <div className="grid gap-4 sm:justify-end">
          <div className="relative overflow-hidden rounded-[2rem] bg-white/5 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur-xl">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.35),_transparent_35%)]" />
            <img
              src="https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80"
              alt="Premium product showcase"
              className="relative h-96 w-full rounded-[1.75rem] object-cover shadow-xl"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
