import { StatusBadge } from "@/components/StatusBadge";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { Plus } from "lucide-react";

const tasks = [
  { id: "a1b2c3d4", name: "Auth middleware", state: "TEST-PASS", confidence: 0.91, updated: "2h ago" },
  { id: "e5f6g7h8", name: "Dashboard filters", state: "CODE", confidence: 0.67, updated: "4h ago" },
  { id: "i9j0k1l2", name: "Rate limiter", state: "TEST-FAIL", confidence: 0.42, updated: "1d ago" },
  { id: "m3n4o5p6", name: "Export pipeline", state: "SPEC", confidence: 0.0, updated: "2d ago" },
  { id: "q7r8s9t0", name: "Session persistence", state: "CERTIFY", confidence: 0.88, updated: "5h ago" },
];

export default function TasksPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Tasks</h1>
          <p className="text-slate-400 mt-1">TDD workflow board</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors">
          <Plus className="h-4 w-4" />
          New task
        </button>
      </header>

      <div className="rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface-overlay text-slate-400 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">State</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {tasks.map((t) => (
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
                <td className="px-4 py-3 text-slate-400">{t.updated}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
