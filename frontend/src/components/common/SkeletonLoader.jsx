function SkeletonLoader({ className = 'h-5 rounded-xl bg-slate-200/70', count = 1 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className={`${className} animate-pulse`} />
      ))}
    </div>
  );
}

export default SkeletonLoader;
