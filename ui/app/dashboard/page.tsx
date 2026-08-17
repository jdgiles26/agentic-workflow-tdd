import { StatusBadge } from "@/components/StatusBadge";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { Play, ShieldCheck, AlertTriangle, Cpu } from "lucide-react";

const stats = [
  { label: "Active tasks", value: "4", icon: Play },
  { label: "Awaiting cert", value: "1", icon: ShieldCheck },
  { label: "Red reports", value: "3", icon: AlertTriangle },
  { label: "Local models", value: "5", icon: Cpu },
];

const recent = [
  { id: "a1b2c3d4", name: "Auth middleware", state: "TEST-PASS", confidence: 0.91 },
  { id: "e5f6g7h8", name: "Dashboard filters", state: "CODE", confidence: 0.67 },
  { id: "i9j0k1l2", name: "Rate limiter", state: "TEST-FAIL", confidence: 0.42 },
  { id: "m3n4o5p6", name: "Export pipeline", state: "SPEC", confidence: 0.0 },
];

export default function DashboardPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-slate-400 mt-1">
          Live multi-agent TDD status · red-before-green enforced
        </p>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className="rounded-xl border border-slate-800 bg-surface-raised p-4"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">{s.label}</span>
                <Icon className="h-4 w-4 text-slate-500" />
              </div>
              <div className="mt-2 text-3xl font-semibold tabular-nums">{s.value}</div>
            </div>
          );
        })}
      </section>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium">Recent tasks</h2>
          <a href="/tasks" className="text-sm text-accent hover:underline">
            View all
          </a>
        </div>
        <div className="rounded-xl border border-slate-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-surface-overlay text-slate-400 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Task</th>
                <th className="px-4 py-3 font-medium">State</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {recent.map((t) => (
                <tr key={t.id} className="hover:bg-surface-overlay/50 transition-colors">
                  <td className="px-4 py-3">
                    <a href={`/tasks/${t.id}`} className="font-medium hover:text-accent">
                      {t.name}
                    </a>
                    <div className="text-xs text-slate-500 font-mono">{t.id}</div>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge state={t.state} />
                  </td>
                  <td className="px-4 py-3">
                    <ConfidenceBar value={t.confidence} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-amber-900/40 bg-amber-950/20 p-4">
        <div className="flex gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-medium text-amber-200">Red-before-green active</div>
            <p className="text-sm text-amber-200/70 mt-1">
              No implementation agent can write under <code className="font-mono text-xs">src/</code> until a valid{" "}
              <code className="font-mono text-xs">red-report.json</code> exists for the task. Ownership and drift
              checks run on every handoff.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
