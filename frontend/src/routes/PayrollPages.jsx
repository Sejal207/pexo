import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useEmployeeQueries } from '../features/employees/useEmployeeQueries';
import {
  useAttachRuleToStructure,
  useComputePayrun,
  useCreatePayrun,
  useCreateSalaryRule,
  useCreateSalaryStructure,
  useEligibleEmployeesMutation,
  useMarkPaidPayrun,
  usePayrollQueries,
  usePayrunDetailQuery,
  usePayslipDetailQuery,
  usePayslipPdfMutation,
  useSalaryStructureDetailQuery,
  useSendPayslips,
  useValidatePayrun,
} from '../features/payroll/usePayrollQueries';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { Pagination } from '../components/Pagination';
import { TableSkeleton, PageLoader } from '../components/Loader';
import { BackButton } from '../components/BackButton';
import { ConfirmModal } from '../components/ConfirmModal';
import { useToast } from '../components/ToastContext';

const Page = ({ children }) => <div className="mx-auto max-w-7xl space-y-6 p-4 sm:p-8">{children}</div>;

const money = (value) => (value === null || value === undefined ? '—' : `₹${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);

const STATUS_COLORS = {
  DRAFT: 'text-slate-400',
  COMPUTED: 'text-amber-400',
  VALIDATED: 'text-sky-400',
  PAID: 'text-emerald-400',
  ERROR: 'text-rose-400',
  CANCELLED: 'text-rose-400',
};

const StatusBadge = ({ status }) => <span className={`font-medium ${STATUS_COLORS[status] || 'text-slate-300'}`}>{status}</span>;

const List = ({ title, headers, rows, loading, error, render, onNew, searchValue, onSearch, page, setPage }) => {
  const term = useDebouncedValue(searchValue || '');
  const filtered = rows.filter((row) => JSON.stringify(row).toLowerCase().includes(term.toLowerCase()));
  const visible = filtered.slice((page - 1) * 10, page * 10);
  return (
    <Page>
      <div className="flex flex-wrap justify-between gap-3">
        <h1 className="text-3xl font-extrabold text-white">{title}</h1>
        {onNew && <button onClick={onNew} className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white">New</button>}
      </div>
      <input
        value={searchValue}
        onChange={(e) => { onSearch(e.target.value); setPage(1); }}
        placeholder={`Search ${title.toLowerCase()}`}
        className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white"
      />
      <div className="overflow-x-auto rounded-lg border border-slate-700/60 bg-slate-800">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr>{headers.map((header) => <th key={header} className="p-4 font-medium">{header}</th>)}</tr>
          </thead>
          <tbody>
            {loading ? <TableSkeleton columns={headers.length} />
              : error ? <tr><td colSpan={headers.length} className="p-6 text-center text-rose-400">Unable to load records.</td></tr>
              : visible.length ? visible.map(render)
              : <tr><td colSpan={headers.length} className="p-6 text-center text-slate-500">No records match your search.</td></tr>}
          </tbody>
        </table>
      </div>
      <Pagination page={page} pageSize={10} total={filtered.length} onPageChange={setPage} />
    </Page>
  );
};

const useEmployeeNameMap = () => {
  const { employeesQuery } = useEmployeeQueries();
  return useMemo(() => {
    const map = new Map();
    (employeesQuery.data || []).forEach((e) => map.set(String(e.id), e.name));
    return map;
  }, [employeesQuery.data]);
};

// ---------------------------------------------------------------------
// Salary Structures
// ---------------------------------------------------------------------

export const SalaryStructuresPage = () => {
  const navigate = useNavigate();
  const { structuresQuery } = usePayrollQueries();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  return (
    <List
      title="Salary Structures"
      headers={['Name', 'Code', 'Description', 'Status']}
      rows={structuresQuery.data || []}
      loading={structuresQuery.isLoading}
      error={structuresQuery.isError}
      searchValue={search}
      onSearch={setSearch}
      page={page}
      setPage={setPage}
      onNew={() => navigate('/payroll/structures/new')}
      render={(row) => (
        <tr key={row.id} onClick={() => navigate(`/payroll/structures/${row.id}`)} className="cursor-pointer border-t border-slate-700/50 hover:bg-slate-700/30">
          <td className="p-4 font-medium text-white">{row.name}</td>
          <td className="p-4 text-slate-300">{row.code}</td>
          <td className="p-4 text-slate-400">{row.description || '—'}</td>
          <td className={row.is_active ? 'p-4 text-emerald-400' : 'p-4 text-slate-500'}>{row.is_active ? 'Active' : 'Inactive'}</td>
        </tr>
      )}
    />
  );
};

export const SalaryStructureDetailPage = () => {
  const { id } = useParams();
  const isNew = id === 'new';
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { rulesQuery } = usePayrollQueries();
  const structureQuery = useSalaryStructureDetailQuery(id);
  const create = useCreateSalaryStructure();
  const attach = useAttachRuleToStructure(id);

  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [ruleToAttach, setRuleToAttach] = useState('');
  const [sequence, setSequence] = useState(10);

  const save = () => create.mutate(
    { name, code, description: description || null, is_active: isActive },
    {
      onSuccess: (structure) => { showToast('Salary structure saved.'); navigate(`/payroll/structures/${structure.id}`); },
      onError: () => showToast('Unable to save salary structure.', 'error'),
    },
  );

  const doAttach = () => attach.mutate(
    { salary_rule_id: ruleToAttach, sequence: Number(sequence) },
    {
      onSuccess: () => { showToast('Rule attached.'); setRuleToAttach(''); },
      onError: () => showToast('Unable to attach rule (sequence or rule may already be used).', 'error'),
    },
  );

  if (isNew) {
    return (
      <Page>
        <BackButton to="/payroll/structures" />
        <h1 className="text-3xl font-extrabold text-white">New Salary Structure</h1>
        <div className="mt-6 space-y-4 rounded-xl border border-slate-700/60 bg-slate-800 p-6">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Code" className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description (optional)" className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
          <label className="flex gap-2 text-slate-200">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />Active
          </label>
          <button disabled={!name || !code || create.isPending} onClick={save} className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white disabled:opacity-50">Save</button>
        </div>
      </Page>
    );
  }

  if (structureQuery.isLoading) return <PageLoader />;
  const structure = structureQuery.data;
  if (!structure) return <Page><BackButton to="/payroll/structures" /><p className="text-rose-400">Salary structure not found.</p></Page>;

  const attachedRuleIds = new Set((structure.rules || []).map((r) => r.salary_rule_id));
  const availableRules = (rulesQuery.data || []).filter((r) => !attachedRuleIds.has(r.id));

  return (
    <Page>
      <BackButton to="/payroll/structures" />
      <h1 className="text-3xl font-extrabold text-white">{structure.name}</h1>
      <p className="text-slate-400">Code: {structure.code} · {structure.is_active ? 'Active' : 'Inactive'}</p>

      <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-6">
        <h2 className="font-semibold text-white">Rules (execution order)</h2>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-slate-400">
              <tr><th className="p-2">Seq</th><th className="p-2">Code</th><th className="p-2">Name</th><th className="p-2">Category</th></tr>
            </thead>
            <tbody>
              {(structure.rules || []).length ? (structure.rules || []).map((r) => (
                <tr key={r.id} className="border-t border-slate-700/50">
                  <td className="p-2 text-slate-300">{r.sequence}</td>
                  <td className="p-2 text-white">{r.rule_code}</td>
                  <td className="p-2 text-slate-300">{r.rule_name}</td>
                  <td className="p-2 text-slate-300">{r.rule_category}</td>
                </tr>
              )) : <tr><td colSpan={4} className="p-4 text-center text-slate-500">No rules attached yet.</td></tr>}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex flex-wrap items-end gap-3 border-t border-slate-700/60 pt-4">
          <div className="flex-1 min-w-[200px]">
            <label className="text-xs text-slate-400">Attach a rule</label>
            <select value={ruleToAttach} onChange={(e) => setRuleToAttach(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 p-2.5 text-white">
              <option value="">Select a rule…</option>
              {availableRules.map((r) => <option key={r.id} value={r.id}>{r.code} — {r.name}</option>)}
            </select>
          </div>
          <div className="w-28">
            <label className="text-xs text-slate-400">Sequence</label>
            <input type="number" value={sequence} onChange={(e) => setSequence(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 p-2.5 text-white" />
          </div>
          <button disabled={!ruleToAttach || attach.isPending} onClick={doAttach} className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white disabled:opacity-50">Attach</button>
        </div>
      </div>
    </Page>
  );
};

// ---------------------------------------------------------------------
// Salary Rules
// ---------------------------------------------------------------------

export const SalaryRulesPage = () => {
  const navigate = useNavigate();
  const { rulesQuery } = usePayrollQueries();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  return (
    <List
      title="Salary Rules"
      headers={['Code', 'Name', 'Category', 'Computation']}
      rows={rulesQuery.data || []}
      loading={rulesQuery.isLoading}
      error={rulesQuery.isError}
      searchValue={search}
      onSearch={setSearch}
      page={page}
      setPage={setPage}
      onNew={() => navigate('/payroll/rules/new')}
      render={(row) => (
        <tr key={row.id} className="border-t border-slate-700/50">
          <td className="p-4 font-medium text-white">{row.code}</td>
          <td className="p-4 text-slate-300">{row.name}</td>
          <td className="p-4 text-slate-300">{row.category}</td>
          <td className="p-4 text-slate-300">{row.computation_type}</td>
        </tr>
      )}
    />
  );
};

const RULE_CATEGORIES = ['BASIC', 'ALLOWANCE', 'GROSS', 'DEDUCTION', 'EMPLOYER_CONTRIBUTION', 'NET'];

export const SalaryRuleDetailPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { rulesQuery } = usePayrollQueries();
  const create = useCreateSalaryRule();
  const [form, setForm] = useState({
    code: '', name: '', category: 'BASIC', computation_type: 'FIXED',
    fixed_amount: '', percentage_of_rule_code: '', percentage_value: '', formula_expression: '',
  });

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const save = () => {
    const payload = {
      code: form.code,
      name: form.name,
      category: form.category,
      computation_type: form.computation_type,
      is_active: true,
    };
    if (form.computation_type === 'FIXED') payload.fixed_amount = Number(form.fixed_amount);
    if (form.computation_type === 'PERCENTAGE') {
      payload.percentage_of_rule_code = form.percentage_of_rule_code;
      payload.percentage_value = Number(form.percentage_value);
    }
    if (form.computation_type === 'FORMULA') payload.formula_expression = form.formula_expression;

    create.mutate(payload, {
      onSuccess: () => { showToast('Salary rule saved.'); navigate('/payroll/rules'); },
      onError: (err) => showToast(err?.response?.data?.detail?.[0]?.msg || 'Unable to save salary rule.', 'error'),
    });
  };

  const canSave = form.code && form.name
    && (form.computation_type === 'FIXED' ? form.fixed_amount !== ''
      : form.computation_type === 'PERCENTAGE' ? form.percentage_of_rule_code && form.percentage_value !== ''
      : form.formula_expression);

  return (
    <Page>
      <BackButton to="/payroll/rules" />
      <h1 className="text-3xl font-extrabold text-white">New Salary Rule</h1>
      <div className="mt-6 grid gap-4 rounded-xl border border-slate-700/60 bg-slate-800 p-6 sm:grid-cols-2">
        <input value={form.code} onChange={set('code')} placeholder="Code (e.g. BASIC, HRA)" className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
        <input value={form.name} onChange={set('name')} placeholder="Name" className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
        <select value={form.category} onChange={set('category')} className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white">
          {RULE_CATEGORIES.map((v) => <option key={v} value={v}>{v}</option>)}
        </select>
        <select value={form.computation_type} onChange={set('computation_type')} className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white">
          <option value="FIXED">Fixed</option>
          <option value="PERCENTAGE">Percentage</option>
          <option value="FORMULA">Formula</option>
        </select>

        {form.computation_type === 'FIXED' && (
          <input type="number" value={form.fixed_amount} onChange={set('fixed_amount')} placeholder="Fixed amount" className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
        )}
        {form.computation_type === 'PERCENTAGE' && (
          <>
            <select value={form.percentage_of_rule_code} onChange={set('percentage_of_rule_code')} className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white">
              <option value="">% of rule…</option>
              {(rulesQuery.data || []).map((r) => <option key={r.code} value={r.code}>{r.code} — {r.name}</option>)}
            </select>
            <input type="number" value={form.percentage_value} onChange={set('percentage_value')} placeholder="Percentage (e.g. 40)" className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
          </>
        )}
        {form.computation_type === 'FORMULA' && (
          <textarea value={form.formula_expression} onChange={set('formula_expression')} placeholder="Formula, e.g. BASIC + HRA, or WAGE for wage capture" className="sm:col-span-2 rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
        )}
        <button disabled={!canSave || create.isPending} onClick={save} className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white disabled:opacity-50 sm:col-span-2">Save</button>
      </div>
    </Page>
  );
};

// ---------------------------------------------------------------------
// Payrun wizard
// ---------------------------------------------------------------------

export const NewPayrunWizard = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { structuresQuery } = usePayrollQueries();
  const eligible = useEligibleEmployeesMutation();
  const create = useCreatePayrun();

  const [step, setStep] = useState(1);
  const [scope, setScope] = useState({ structure: '', start: '', end: '' });
  const [selected, setSelected] = useState([]);

  const continueToStep2 = () => {
    eligible.mutate(
      { salary_structure_id: scope.structure, period_start: scope.start, period_end: scope.end },
      {
        onSuccess: (rows) => { setSelected(rows.map((r) => r.employee_id)); setStep(2); },
        onError: () => showToast('Unable to load eligible employees for this period/structure.', 'error'),
      },
    );
  };

  const toggle = (employeeId) => setSelected((ids) => (ids.includes(employeeId) ? ids.filter((item) => item !== employeeId) : [...ids, employeeId]));

  const submit = () => create.mutate(
    {
      salary_structure_id: scope.structure,
      period_start: scope.start,
      period_end: scope.end,
      employee_ids: selected,
    },
    {
      onSuccess: (payrun) => { showToast('Payrun created.'); navigate(`/payroll/payruns/${payrun.id}`); },
      onError: (err) => showToast(err?.response?.data?.detail || 'Unable to create payrun.', 'error'),
    },
  );

  const rows = eligible.data || [];

  return (
    <Page>
      <BackButton to="/payroll/payruns" />
      <h1 className="text-3xl font-extrabold text-white">New Payrun</h1>
      <p className="text-slate-400">Step {step} of 2</p>

      {step === 1 ? (
        <div className="mt-6 grid gap-4 rounded-xl border border-slate-700/60 bg-slate-800 p-6 sm:grid-cols-2">
          <select value={scope.structure} onChange={(e) => setScope({ ...scope, structure: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white">
            <option value="">Salary structure</option>
            {(structuresQuery.data || []).filter((s) => s.is_active).map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}
          </select>
          <div />
          <input type="date" value={scope.start} onChange={(e) => setScope({ ...scope, start: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
          <input type="date" value={scope.end} onChange={(e) => setScope({ ...scope, end: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-white" />
          <button
            disabled={!scope.structure || !scope.start || !scope.end || eligible.isPending}
            onClick={continueToStep2}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white disabled:opacity-50"
          >
            {eligible.isPending ? 'Checking eligibility…' : 'Continue'}
          </button>
        </div>
      ) : (
        <div className="mt-6 overflow-x-auto rounded-xl border border-slate-700/60 bg-slate-800 p-4">
          <p className="mb-3 text-sm text-slate-400">Select eligible employees. No payrun is created until you click Create Payrun.</p>
          <table className="w-full text-sm">
            <thead className="text-left text-slate-400">
              <tr><th className="p-3"></th><th className="p-3">Employee</th><th className="p-3">Working Hours</th><th className="p-3">Start Date</th><th className="p-3">Wage</th></tr>
            </thead>
            <tbody>
              {rows.length ? rows.map((employee) => (
                <tr key={employee.employee_id} className="border-t border-slate-700/50">
                  <td className="p-3"><input type="checkbox" checked={selected.includes(employee.employee_id)} onChange={() => toggle(employee.employee_id)} /></td>
                  <td className="p-3 text-white">{employee.employee_name} <span className="text-slate-500">({employee.employee_code})</span></td>
                  <td className="p-3 text-slate-300">{employee.working_hours ?? '—'}</td>
                  <td className="p-3 text-slate-300">{employee.start_date}</td>
                  <td className="p-3 text-amber-400">{money(employee.wage_amount)} / {employee.wage_type}</td>
                </tr>
              )) : <tr><td colSpan={5} className="p-6 text-center text-slate-500">No eligible employees for this period and structure.</td></tr>}
            </tbody>
          </table>
          <div className="mt-4 flex gap-3">
            <button onClick={() => setStep(1)} className="rounded-lg border border-slate-600 px-4 py-2 text-slate-200">Back</button>
            <button disabled={!selected.length || create.isPending} onClick={submit} className="rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white disabled:opacity-50">Create Payrun</button>
          </div>
        </div>
      )}
    </Page>
  );
};

// ---------------------------------------------------------------------
// Payruns
// ---------------------------------------------------------------------

export const PayrunsPage = () => {
  const navigate = useNavigate();
  const { payrunsQuery } = usePayrollQueries();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  return (
    <List
      title="Payruns"
      headers={['Name / period', 'Status', 'Paid at']}
      rows={payrunsQuery.data || []}
      loading={payrunsQuery.isLoading}
      error={payrunsQuery.isError}
      searchValue={search}
      onSearch={setSearch}
      page={page}
      setPage={setPage}
      onNew={() => navigate('/payroll/payruns/new')}
      render={(row) => (
        <tr key={row.id} onClick={() => navigate(`/payroll/payruns/${row.id}`)} className="cursor-pointer border-t border-slate-700/50 hover:bg-slate-700/30">
          <td className="p-4 font-medium text-white">{row.name}<span className="ml-2 text-slate-400">{row.period_start} – {row.period_end}</span></td>
          <td className="p-4"><StatusBadge status={row.status} /></td>
          <td className="p-4 text-slate-400">{row.paid_at ? new Date(row.paid_at).toLocaleDateString() : '—'}</td>
        </tr>
      )}
    />
  );
};

const ACTION_FLOW = {
  DRAFT: { label: 'Compute', next: 'COMPUTED' },
  COMPUTED: { label: 'Validate', next: 'VALIDATED' },
  VALIDATED: { label: 'Mark Paid', next: 'PAID' },
};

export const PayrunDetailPage = () => {
  const { id } = useParams();
  const { showToast } = useToast();
  const payrunQuery = usePayrunDetailQuery(id);
  const employeeNames = useEmployeeNameMap();
  const compute = useComputePayrun();
  const validate = useValidatePayrun();
  const markPaid = useMarkPaidPayrun();
  const sendPayslips = useSendPayslips();
  const [warningModal, setWarningModal] = useState(null);

  if (payrunQuery.isLoading) return <PageLoader />;
  const payrun = payrunQuery.data;
  if (!payrun) return <Page><BackButton to="/payroll/payruns" /><p className="text-rose-400">Payrun not found.</p></Page>;

  const status = payrun.status;
  const busy = compute.isPending || validate.isPending || markPaid.isPending || sendPayslips.isPending;

  const runCompute = () => compute.mutate(id, {
    onSuccess: (res) => {
      const failed = (res.results || []).filter((r) => r.status === 'ERROR');
      showToast(failed.length ? `Computed with ${failed.length} error(s) — check payslips.` : 'Payrun computed.', failed.length ? 'error' : 'success');
    },
    onError: () => showToast('Unable to compute payrun.', 'error'),
  });

  const runValidate = () => validate.mutate(id, {
    onSuccess: (res) => {
      const blocking = (res.results || []).filter((r) => r.blocking);
      if (blocking.length) {
        setWarningModal(blocking.map((b) => `${employeeNames.get(String(b.employee_id)) || b.employee_id}: ${b.warnings.join('; ')}`));
      } else {
        showToast('Payrun validated — ready to mark paid.');
      }
    },
    onError: () => showToast('Unable to validate payrun.', 'error'),
  });

  const runMarkPaid = () => markPaid.mutate(id, {
    onSuccess: () => showToast('Marked paid — payslip PDFs are generating in the background.'),
    onError: (err) => showToast(err?.response?.data?.detail ? String(err.response.data.detail) : 'Mark Paid blocked by outstanding warnings.', 'error'),
  });

  const runSend = () => sendPayslips.mutate(id, {
    onSuccess: () => showToast('Payslip emails queued.'),
    onError: () => showToast('Unable to send payslips.', 'error'),
  });

  const actionFor = {
    Compute: runCompute,
    Validate: runValidate,
    'Mark Paid': runMarkPaid,
  };
  const currentAction = ACTION_FLOW[status];

  return (
    <Page>
      <BackButton to="/payroll/payruns" />
      <h1 className="text-3xl font-extrabold text-white">{payrun.name}</h1>
      <p className="text-slate-400">{payrun.period_start} – {payrun.period_end} · <StatusBadge status={status} /></p>

      <div className="flex flex-wrap gap-3">
        <button
          disabled={!currentAction || busy}
          onClick={() => currentAction && actionFor[currentAction.label]()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-40"
        >
          {currentAction ? currentAction.label : 'Compute'}
        </button>
        <button disabled={status !== 'PAID' || busy} onClick={runSend} className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-200 disabled:opacity-40">Send Payslips</button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-700/60 bg-slate-800">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="p-4">Employee</th><th className="p-4">Gross</th><th className="p-4">Net</th><th className="p-4">Warning</th><th className="p-4">Status</th></tr>
          </thead>
          <tbody>
            {(payrun.payslips || []).map((item) => (
              <tr key={item.id} className="cursor-pointer border-t border-slate-700/50 hover:bg-slate-700/30" onClick={() => window.location.assign(`/payroll/payslips/${item.id}`)}>
                <td className="p-4 text-white">{employeeNames.get(String(item.employee_id)) || item.employee_id}</td>
                <td className="p-4 text-amber-400">{money(item.gross_amount)}</td>
                <td className="p-4 text-emerald-400">{money(item.net_amount)}</td>
                <td className="p-4 text-rose-400">{item.has_warning ? (item.warning_notes || 'Warning') : '—'}</td>
                <td className="p-4"><StatusBadge status={item.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmModal
        open={Boolean(warningModal)}
        title="Validation warnings"
        items={warningModal || []}
        confirmLabel="Close"
        onConfirm={() => setWarningModal(null)}
        onCancel={() => setWarningModal(null)}
      />
    </Page>
  );
};

// ---------------------------------------------------------------------
// Payslips
// ---------------------------------------------------------------------

export const PayslipsPage = () => {
  const navigate = useNavigate();
  const { payslipsQuery } = usePayrollQueries();
  const employeeNames = useEmployeeNameMap();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const rows = (payslipsQuery.data || []).map((row) => ({ ...row, _employeeName: employeeNames.get(String(row.employee_id)) || row.employee_id }));
  return (
    <List
      title="Payslips"
      headers={['Employee', 'Period', 'Gross', 'Net', 'Status']}
      rows={rows}
      loading={payslipsQuery.isLoading}
      error={payslipsQuery.isError}
      searchValue={search}
      onSearch={setSearch}
      page={page}
      setPage={setPage}
      render={(row) => (
        <tr key={row.id} onClick={() => navigate(`/payroll/payslips/${row.id}`)} className="cursor-pointer border-t border-slate-700/50 hover:bg-slate-700/30">
          <td className="p-4 font-medium text-white">{row._employeeName}</td>
          <td className="p-4 text-slate-300">{row.period_start} – {row.period_end}</td>
          <td className="p-4 text-amber-400">{money(row.gross_amount)}</td>
          <td className="p-4 text-emerald-400">{money(row.net_amount)}</td>
          <td className="p-4"><StatusBadge status={row.status} /></td>
        </tr>
      )}
    />
  );
};

export const PayslipDetailPage = () => {
  const { id } = useParams();
  const { showToast } = useToast();
  const payslipQuery = usePayslipDetailQuery(id);
  const employeeNames = useEmployeeNameMap();
  const pdfMutation = usePayslipPdfMutation();

  if (payslipQuery.isLoading) return <PageLoader />;
  const slip = payslipQuery.data;
  if (!slip) return <Page><BackButton to="/payroll/payslips" /><p className="text-rose-400">Payslip not found.</p></Page>;

  const printPayslip = () => pdfMutation.mutate(id, {
    onSuccess: (res) => window.open(res.pdf_url, '_blank'),
    onError: () => showToast('PDF generation failed — the payroll worker may not be running.', 'error'),
  });

  return (
    <Page>
      <BackButton to="/payroll/payslips" />
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h1 className="text-3xl font-extrabold text-white">Payslip — {employeeNames.get(String(slip.employee_id)) || slip.employee_id}</h1>
          <p className="mt-1 text-slate-400">{slip.period_start} – {slip.period_end} · <StatusBadge status={slip.status} /></p>
        </div>
        <button disabled={pdfMutation.isPending} onClick={printPayslip} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">
          {pdfMutation.isPending ? 'Generating…' : 'Print Payslip'}
        </button>
      </div>

      {slip.has_warning && <p className="rounded-lg border border-rose-700 bg-rose-950/40 p-3 text-sm text-rose-300">{slip.warning_notes}</p>}

      <div className="overflow-x-auto rounded-xl border border-slate-700/60 bg-slate-800">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="p-4">Rule</th><th className="p-4">Category</th><th className="p-4">Amount</th></tr>
          </thead>
          <tbody>
            {(slip.lines || []).map((line) => (
              <tr key={line.id} className="border-t border-slate-700/50">
                <td className="p-4 text-white">{line.rule_name || line.salary_rule_code}</td>
                <td className="p-4 text-slate-300">{line.category || '—'}</td>
                <td className="p-4 text-amber-400">{money(line.amount)}</td>
              </tr>
            ))}
            <tr className="border-t-2 border-slate-600">
              <td colSpan="2" className="p-4 font-semibold text-white">Gross total</td>
              <td className="p-4 font-bold text-amber-400">{money(slip.gross_amount)}</td>
            </tr>
            <tr>
              <td colSpan="2" className="p-4 font-semibold text-white">Net total</td>
              <td className="p-4 font-bold text-emerald-400">{money(slip.net_amount)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Page>
  );
};

// ---------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------

export const PayrollDashboardPage = () => {
  const { payslipsQuery, payrunsQuery } = usePayrollQueries();
  const slips = payslipsQuery.data || [];
  const paidSlips = slips.filter((s) => s.status === 'PAID');
  const totalNet = paidSlips.reduce((sum, row) => sum + Number(row.net_amount || 0), 0);
  const kpis = [
    ['Total Net Salary Paid', money(totalNet)],
    ['Payslips Generated', slips.length],
    ['Payslips Paid', paidSlips.length],
    ['Average Net (Paid)', paidSlips.length ? money(totalNet / paidSlips.length) : '—'],
    ['Payruns', (payrunsQuery.data || []).length],
  ];
  return (
    <Page>
      <h1 className="text-3xl font-extrabold text-white">Payroll Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {kpis.map(([label, value]) => (
          <div key={label} className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
            <p className="text-sm text-slate-400">{label}</p>
            <p className="mt-2 text-2xl font-bold text-white">{value}</p>
          </div>
        ))}
      </div>
      <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
        <h2 className="font-semibold text-white">Payslip Status</h2>
        <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-300">
          {['DRAFT', 'COMPUTED', 'VALIDATED', 'PAID', 'ERROR'].map((s) => (
            <span key={s}><StatusBadge status={s} /> — {slips.filter((slip) => slip.status === s).length}</span>
          ))}
        </div>
      </div>
    </Page>
  );
};
