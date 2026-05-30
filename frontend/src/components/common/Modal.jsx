function Modal({ title, open, onClose, children, footer }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6">
      <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl ring-1 ring-black/10">
        <div className="flex items-center justify-between gap-4 border-b border-gray-200 pb-4">
          <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-900">Close</button>
        </div>
        <div className="mt-5">{children}</div>
        {footer && <div className="mt-6 border-t border-gray-200 pt-4">{footer}</div>}
      </div>
    </div>
  );
}

export default Modal;
