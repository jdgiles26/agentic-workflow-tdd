"use client";

import { useEffect, useState } from "react";
import { Cpu, CheckCircle2, XCircle } from "lucide-react";
import { listModels, type ModelInfo } from "@/lib/api";

export default function ModelsPage() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listModels()
      .then(setModels)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to discover models"));
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Local Models</h1>
        <p className="text-slate-400 mt-1">Discovered from Ollama · llama.cpp · MLX</p>
      </header>
      {error ? <p className="text-sm text-status-fail">{error}</p> : null}

      <div className="rounded-xl border border-slate-800 overflow-hidden">
        {models.length === 0 && !error ? (
          <p className="px-4 py-8 text-sm text-slate-500">No backends responded. Start Ollama or llama-server.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-surface-overlay text-slate-400 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Model</th>
                <th className="px-4 py-3 font-medium">Backend</th>
                <th className="px-4 py-3 font-medium">Size</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {models.map((m) => (
                <tr key={m.id} className="hover:bg-surface-overlay/50">
                  <td className="px-4 py-3">
                    <div className="font-medium flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-slate-500" />
                      {m.name}
                    </div>
                    <div className="text-xs text-slate-500 font-mono mt-0.5">{m.id}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{m.backend}</td>
                  <td className="px-4 py-3 tabular-nums text-slate-400">
                    {m.size_gb != null ? `${m.size_gb.toFixed(1)} GB` : "—"}
                  </td>
                  <td className="px-4 py-3">
                    {m.available ? (
                      <span className="inline-flex items-center gap-1.5 text-status-pass text-xs">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Available
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-slate-500 text-xs">
                        <XCircle className="h-3.5 w-3.5" /> Offline
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
