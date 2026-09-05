import { useState, useEffect } from 'react';
import { X, Save, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useUpdateEmployee } from '../useEmployeeQueries';

const STATUS_OPTIONS = [
  { value: 'ACTIVE', label: 'Active' },
  { value: 'INACTIVE', label: 'Inactive' },
  { value: 'TERMINATED', label: 'Terminated' },
  { value: 'ON_LEAVE', label: 'On Leave' },
];

const GENDER_OPTIONS = [
  { value: '', label: 'Not specified' },
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
  { value: 'Other', label: 'Other' },
];

function Field({ label, id, children }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">
        {label}
      </label>
      {children}
    </div>
  );
}

const inputCls =
  'w-full rounded-lg bg-slate-900 border border-slate-700/60 px-3 py-2.5 text-sm text-white ' +
  'placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/40 transition-colors';

const selectCls =
  'w-full rounded-lg bg-slate-900 border border-slate-700/60 px-3 py-2.5 text-sm text-white ' +
  'focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/40 transition-colors appearance-none';

export function EditEmployeeDrawer({ employee, open, onClose }) {
  const updateMutation = useUpdateEmployee(employee?.id);

  const [tab, setTab] = useState('work');
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    gender: '',
    employment_status: 'ACTIVE',
    address_line: '',
    city: '',
    state: '',
    pincode: '',
    date_exit: '',
  });

  // Sync form when employee data or drawer open state changes
  useEffect(() => {
    if (employee && open) {
      setForm({
        first_name: employee.first_name || '',
        last_name: employee.last_name || '',
        phone: employee.phone || '',
        gender: employee.gender || '',
        employment_status: employee.employment_status || employee.employmentStatus || 'ACTIVE',
        address_line: employee.address_line || employee.addressLine || '',
        city: employee.city || '',
        state: employee.state || '',
        pincode: employee.pincode || '',
        date_exit: employee.date_exit || employee.dateExit || '',
      });
      setTab('work');
    }
  }, [employee, open]);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSave = async () => {
    // Build only non-null diff payload
    const payload = Object.fromEntries(
      Object.entries(form).filter(([, v]) => v !== '' && v !== null && v !== undefined)
    );
    // Ensure nulls are sent for cleared date_exit
    if (form.date_exit === '') payload.date_exit = null;
    try {
      await updateMutation.mutateAsync(payload);
      setTimeout(() => onClose(), 800);
    } catch (_) {
      // Error shown via mutation state
    }
  };

  if (!open) return null;

  const isSaving = updateMutation.isPending;
  const isSuccess = updateMutation.isSuccess;
  const isError = updateMutation.isError;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Edit Employee"
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-lg flex-col bg-slate-850 shadow-2xl
                   border-l border-slate-700/60"
        style={{ background: '#0f172a' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-700/60">
          <div>
            <h2 className="text-lg font-bold text-white">Edit Employee</h2>
            <p className="text-xs text-slate-400 mt-0.5">{employee?.employee_code} · {employee?.email}</p>
          </div>
          <button
            id="edit-drawer-close"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-0 border-b border-slate-700/60 px-6">
          {['work', 'personal'].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`py-3 px-1 mr-6 text-sm font-medium border-b-2 transition-colors capitalize ${
                tab === t
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              {t === 'work' ? 'Work Information' : 'Personal Details'}
            </button>
          ))}
        </div>

        {/* Form body */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {tab === 'work' && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <Field label="First Name" id="ef-first-name">
                  <input
                    id="ef-first-name"
                    className={inputCls}
                    value={form.first_name}
                    onChange={set('first_name')}
                    placeholder="First name"
                  />
                </Field>
                <Field label="Last Name" id="ef-last-name">
                  <input
                    id="ef-last-name"
                    className={inputCls}
                    value={form.last_name}
                    onChange={set('last_name')}
                    placeholder="Last name"
                  />
                </Field>
              </div>

              <Field label="Phone" id="ef-phone">
                <input
                  id="ef-phone"
                  className={inputCls}
                  value={form.phone}
                  onChange={set('phone')}
                  placeholder="+1 555 000 0000"
                />
              </Field>

              <Field label="Employment Status" id="ef-status">
                <div className="relative">
                  <select
                    id="ef-status"
                    className={selectCls}
                    value={form.employment_status}
                    onChange={set('employment_status')}
                  >
                    {STATUS_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                  <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">▾</span>
                </div>
              </Field>

              <Field label="Exit Date" id="ef-exit">
                <input
                  id="ef-exit"
                  type="date"
                  className={inputCls}
                  value={form.date_exit}
                  onChange={set('date_exit')}
                />
              </Field>

              <div className="rounded-lg bg-slate-800/50 border border-slate-700/40 p-4 text-xs text-slate-400 leading-relaxed">
                <strong className="text-slate-300">Read-only fields</strong><br />
                Employee code, work email, and date of joining are managed by HR and cannot be changed from this form.
              </div>
            </>
          )}

          {tab === 'personal' && (
            <>
              <Field label="Gender" id="ef-gender">
                <div className="relative">
                  <select
                    id="ef-gender"
                    className={selectCls}
                    value={form.gender}
                    onChange={set('gender')}
                  >
                    {GENDER_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                  <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">▾</span>
                </div>
              </Field>

              <Field label="Address" id="ef-address">
                <input
                  id="ef-address"
                  className={inputCls}
                  value={form.address_line}
                  onChange={set('address_line')}
                  placeholder="Street address"
                />
              </Field>

              <div className="grid grid-cols-2 gap-4">
                <Field label="City" id="ef-city">
                  <input
                    id="ef-city"
                    className={inputCls}
                    value={form.city}
                    onChange={set('city')}
                    placeholder="City"
                  />
                </Field>
                <Field label="State" id="ef-state">
                  <input
                    id="ef-state"
                    className={inputCls}
                    value={form.state}
                    onChange={set('state')}
                    placeholder="State"
                  />
                </Field>
              </div>

              <Field label="Pincode / ZIP" id="ef-pincode">
                <input
                  id="ef-pincode"
                  className={inputCls}
                  value={form.pincode}
                  onChange={set('pincode')}
                  placeholder="000000"
                />
              </Field>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between gap-3 px-6 py-4 border-t border-slate-700/60">
          {/* Status feedback */}
          <div className="text-sm">
            {isSaving && (
              <span className="flex items-center gap-2 text-slate-400">
                <Loader2 className="w-4 h-4 animate-spin" /> Saving…
              </span>
            )}
            {isSuccess && (
              <span className="flex items-center gap-2 text-emerald-400">
                <CheckCircle className="w-4 h-4" /> Saved successfully
              </span>
            )}
            {isError && (
              <span className="flex items-center gap-2 text-rose-400">
                <AlertCircle className="w-4 h-4" />
                {updateMutation.error?.response?.data?.detail || 'Save failed'}
              </span>
            )}
          </div>

          <div className="flex gap-3">
            <button
              id="edit-drawer-cancel"
              onClick={onClose}
              disabled={isSaving}
              className="px-4 py-2.5 rounded-lg border border-slate-700 text-slate-300 text-sm font-medium
                         hover:bg-slate-800 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              id="edit-drawer-save"
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500
                         text-white text-sm font-semibold transition-colors disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Save Changes
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
