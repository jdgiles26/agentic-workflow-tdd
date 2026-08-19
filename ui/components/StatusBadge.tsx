import { clsx } from "clsx";

const map: Record<string, string> = {
  SPEC: "bg-status-spec/20 text-status-spec border-status-spec/40",
  "TEST-FAIL": "bg-status-fail/20 text-status-fail border-status-fail/40",
  CODE: "bg-status-code/20 text-status-code border-status-code/40",
  "TEST-PASS": "bg-status-pass/20 text-status-pass border-status-pass/40",
  CERTIFY: "bg-status-certify/20 text-status-certify border-status-certify/40",
  DONE: "bg-status-done/20 text-status-done border-status-done/40",
  REJECTED: "bg-status-rejected/20 text-status-rejected border-status-rejected/40",
};

export function StatusBadge({ state }: { state: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        map[state] ?? "bg-slate-700 text-slate-300"
      )}
    >
      {state}
    </span>
  );
}
