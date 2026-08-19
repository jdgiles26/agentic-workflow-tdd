"use client";

import { useEffect, useState } from "react";
import { health } from "@/lib/api";

export default function SettingsPage() {
  const [status, setStatus] = useState("checking…");

  useEffect(() => {
    health()
      .then((h) => setStatus(`ok · API ${h.version}`))
      .catch(() => setStatus("offline — start `uvicorn api.main:app --port 8000`"));
  }, []);

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-slate-400 mt-1">Local API and model backends</p>
      </header>
      <dl className="rounded-xl border border-slate-800 divide-y divide-slate-800">
        <div className="px-4 py-3 flex justify-between gap-4">
          <dt className="text-slate-400">API</dt>
          <dd className="font-mono text-sm">{status}</dd>
        </div>
        <div className="px-4 py-3 flex justify-between gap-4">
          <dt className="text-slate-400">Proxy</dt>
          <dd className="font-mono text-sm">/api/* → 127.0.0.1:8000</dd>
        </div>
        <div className="px-4 py-3 flex justify-between gap-4">
          <dt className="text-slate-400">Store</dt>
          <dd className="font-mono text-sm">workflow_store.json</dd>
        </div>
      </dl>
    </div>
  );
}
