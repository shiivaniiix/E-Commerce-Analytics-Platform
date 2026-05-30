function Sidebar({ children }) {
  return (
    <aside className="hidden min-h-[calc(100vh-120px)] w-72 space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:block">
      {children}
    </aside>
  );
}

export default Sidebar;
