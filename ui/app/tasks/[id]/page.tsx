"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { StatusBadge } from "@/components/StatusBadge";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { attachRedReport, certifyTask, getTask, updateTask, type Task } from "@/lib/api";

export default function TaskDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [task, setTask] = useState<Task | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = () =>
    getTask(id)
      .then(setTask)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Not found"));

  useEffect(() => {
    void refresh();
  }, [id]);

  const saveField = async (field: "spec" | "tests", value: string) => {
    setBusy(true);
    try {
      setTask(await updateTask(id, { [field]: value }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  };

  const onRed = async () => {
    setBusy(true);
    try {
      setTask(await attachRedReport(id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Red report failed");
    } finally {
      setBusy(false);
    }
  };

  const onCertify = async (approved: boolean) => {
    setBusy(true);
    try {
      setTask(await certifyTask(id, approved, notes));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Certify failed");
    } finally {
      setBusy(false);
    }
  };

  if (!task) {
    return <div className="p-8 text-slate-400">{error ?? "Loading…"}</div>;
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <header className="space-y-2">
        <a href="/tasks" className="text-sm text-accent hover:underline">
          ← Tasks
        </a>
        <div className="flex items-center justify-between gap-4">
          <h1 className="text-2xl font-semibold tracking-tight">{task.name}</h1>
          <StatusBadge state={task.state} />
        </div>
        <p className="text-slate-400 text-sm">{task.description || "No description"}</p>
        <ConfidenceBar value={task.confidence} />
      </header>
      {error ? <p className="text-sm text-status-fail">{error}</p> : null}

      <section className="space-y-2">
        <h2 className="font-medium">Spec</h2>
        <textarea
          className="w-full min-h-[120px] rounded-lg border border-slate-800 bg-surface-raised p-3 text-sm"
          defaultValue={task.spec}
          onBlur={(e) => void saveField("spec", e.target.value)}
        />
      </section>

      <section className="space-y-2">
        <h2 className="font-medium">Tests</h2>
        <textarea
          className="w-full min-h-[160px] rounded-lg border border-slate-800 bg-surface-raised p-3 text-sm font-mono"
          defaultValue={task.tests}
          onBlur={(e) => void saveField("tests", e.target.value)}
        />
        <button
          type="button"
          disabled={busy || !task.tests.trim()}
          onClick={() => void onRed()}
          className="rounded-lg border border-amber-700 px-3 py-1.5 text-sm text-amber-200 hover:bg-amber-950/40 disabled:opacity-50"
        >
          Run controlled pytest → attach red report
        </button>
        {task.red_report_path ? (
          <p className="text-xs text-slate-500 font-mono">{task.red_report_path}</p>
        ) : null}
      </section>

      <section className="space-y-2">
        <h2 className="font-medium">Code</h2>
        <pre className="rounded-lg border border-slate-800 bg-surface-raised p-3 text-sm font-mono whitespace-pre-wrap text-slate-300 min-h-[80px]">
          {task.code || "(implementation locked until CODE)"}
        </pre>
      </section>

      {task.state === "CERTIFY" ? (
        <section className="rounded-xl border border-slate-800 bg-surface-raised p-5 space-y-3">
          <h2 className="font-medium">HITL certification</h2>
          <textarea
            className="w-full min-h-[80px] rounded-lg border border-slate-800 bg-void p-3 text-sm"
            placeholder="Certification notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          <div className="flex gap-3">
            <button
              type="button"
              disabled={busy}
              onClick={() => void onCertify(true)}
              className="rounded-lg bg-accent px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              Approve → DONE
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void onCertify(false)}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm disabled:opacity-50"
            >
              Reject → SPEC
            </button>
          </div>
        </section>
      ) : null}

      <section>
        <h2 className="font-medium mb-2">History</h2>
        <ul className="text-sm text-slate-400 space-y-1">
          {task.history.map((h, i) => (
            <li key={`${h.at}-${i}`} className="font-mono text-xs">
              {h.from} → {h.to} · {h.notes}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
