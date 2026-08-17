import { Cpu, CheckCircle2, XCircle } from "lucide-react";

const models = [
  { id: "ollama:llama3.1:8b", name: "llama3.1:8b", backend: "Ollama", available: true, size: "4.7 GB" },
  { id: "ollama:codellama:7b", name: "codellama:7b", backend: "Ollama", available: true, size: "3.8 GB" },
  { id: "llamacpp:qwen2.5-coder-7b-q4", name: "Qwen2.5-Coder 7B Q4", backend: "llama.cpp", available: true, size: "4.1 GB" },
  { id: "mlx:mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", name: "Llama-3.1-8B 4bit", backend: "MLX", available: false, size: "—" },
  { id: "ollama:mistral:7b", name: "mistral:7b", backend: "Ollama", available: true, size: "4.1 GB" },
];

export default function ModelsPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Local Models</h1>
        <p className="text-slate-400 mt-1">
          Drop-in backends: Ollama · llama.cpp (GGUF) · MLX
        </p>
      </header>

      <div className="rounded-xl border border-slate-800 overflow-hidden">
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
                <td className="px-4 py-3 tabular-nums text-slate-400">{m.size}</td>
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
      </div>

      <div className="rounded-xl border border-slate-800 bg-surface-raised p-5 space-y-3">
        <h2 className="font-medium">Quick start</h2>
        <ul className="text-sm text-slate-400 space-y-2 list-disc list-inside">
          <li>
            <strong className="text-slate-200">Ollama</strong> —{" "}
            <code className="font-mono text-xs">ollama serve</code> then pull models
          </li>
          <li>
            <strong className="text-slate-200">llama.cpp</strong> — start{" "}
            <code className="font-mono text-xs">llama-server --model your.gguf</code> on :8080
          </li>
          <li>
            <strong className="text-slate-200">MLX</strong> — Apple Silicon only; install{" "}
            <code className="font-mono text-xs">mlx-lm</code>
          </li>
        </ul>
      </div>
    </div>
  );
}
