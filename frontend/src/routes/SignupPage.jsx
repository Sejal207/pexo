import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { httpClient } from '../api/httpClient';
import { useToast } from '../components/ToastContext';

export const SignupPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirmPassword: '' });
  const [saving, setSaving] = useState(false);
  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value });
  const submit = async (event) => {
    event.preventDefault();
    if (form.password !== form.confirmPassword) { showToast('Passwords do not match.', 'error'); return; }
    setSaving(true);
    try {
      await httpClient.post('/auth/signup', { full_name: form.full_name, email: form.email, password: form.password });
      showToast('Account created. You can now sign in.');
      navigate('/login');
    } catch (error) {
      const message = error?.response?.data?.detail || 'Unable to create your account.';
      showToast(message, 'error');
    } finally { setSaving(false); }
  };
  return <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-md items-center p-4"><form onSubmit={submit} className="w-full space-y-5 rounded-2xl border border-slate-700/60 bg-slate-800 p-6 shadow-xl"><div><h1 className="text-3xl font-extrabold text-white">Create your account</h1><p className="mt-1 text-sm text-slate-400">Join Pexo to manage your HR, time, and payroll work.</p></div><label className="block text-sm text-slate-300">Full name<input required value={form.full_name} onChange={update('full_name')} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" /></label><label className="block text-sm text-slate-300">Email<input required type="email" value={form.email} onChange={update('email')} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" /></label><label className="block text-sm text-slate-300">Password<input required minLength="8" type="password" value={form.password} onChange={update('password')} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" /></label><label className="block text-sm text-slate-300">Confirm password<input required type="password" value={form.confirmPassword} onChange={update('confirmPassword')} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" /></label><button disabled={saving} className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50">{saving ? 'Creating account…' : 'Sign up'}</button><p className="text-center text-sm text-slate-400">Already have an account? <Link to="/login" className="font-medium text-indigo-400 hover:text-indigo-300">Sign in</Link></p></form></div>;
};
export default SignupPage;
