import { clsx } from "clsx";

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)));
  const color =
    pct >= 80 ? "bg-status-pass" : pct >= 50 ? "bg-status-code" : "bg-status-fail";

  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 rounded-full bg-slate-800 overflow-hidden">
        <div className={clsx("h-full rounded-full transition-all", color)} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs tabular-nums text-slate-400">{pct}%</span>
    </div>
  );
}
