import { createContext, useContext, useMemo, useState } from 'react';
const ToastContext = createContext({ showToast: () => {} });
export const ToastProvider = ({ children }) => { const [toasts, setToasts] = useState([]); const value = useMemo(() => ({ showToast: (message, type = 'success') => { const id = Date.now(); setToasts((items) => [...items, { id, message, type }]); window.setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), 4000); } }), []); return <ToastContext.Provider value={value}>{children}<div className="fixed bottom-4 right-4 z-[110] space-y-2">{toasts.map((toast) => <div key={toast.id} className={`rounded-lg px-4 py-3 text-sm shadow-lg ${toast.type === 'error' ? 'bg-rose-600 text-white' : 'bg-emerald-600 text-white'}`}>{toast.message}</div>)}</div></ToastContext.Provider>; };
// eslint-disable-next-line react-refresh/only-export-components
export const useToast = () => useContext(ToastContext);
