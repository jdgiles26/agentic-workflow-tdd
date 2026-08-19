"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { StatusBadge } from "@/components/StatusBadge";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { Plus } from "lucide-react";
import { createTask, listTasks, relativeTime, type Task } from "@/lib/api";

export default function TasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const refresh = () =>
    listTasks()
      .then(setTasks)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load tasks"));

  useEffect(() => {
    void refresh();
  }, []);

  const onCreate = async () => {
    const name = window.prompt("Task name");
    if (!name?.trim()) return;
    setCreating(true);
    try {
      const task = await createTask(name.trim());
      router.push(`/tasks/${task.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Tasks</h1>
          <p className="text-slate-400 mt-1">TDD workflow board</p>
        </div>
        <button
          type="button"
          onClick={() => void onCreate()}
          disabled={creating}
          className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
          New task
        </button>
      </header>
      {error ? <p className="text-sm text-status-fail">{error}</p> : null}

      <div className="rounded-xl border border-slate-800 overflow-hidden">
        {tasks.length === 0 ? (
          <p className="px-4 py-8 text-sm text-slate-500">No tasks. Create one to start SPEC → TEST-FAIL.</p>
        ) : (
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
                  <td className="px-4 py-3 text-slate-400">{relativeTime(t.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
