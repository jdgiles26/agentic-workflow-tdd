"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, ListTodo, Cpu, Settings, Shield } from "lucide-react";
import { clsx } from "clsx";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/tasks", label: "Tasks", icon: ListTodo },
  { href: "/models", label: "Models", icon: Cpu },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 shrink-0 border-r border-slate-800 bg-surface-raised flex flex-col">
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-accent" />
          <div>
            <div className="font-semibold tracking-tight">AWT</div>
            <div className="text-xs text-slate-500">Agentic TDD</div>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {nav.map((item) => {
          const active = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-accent-muted text-white"
                  : "text-slate-400 hover:bg-surface-overlay hover:text-slate-200"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
        Red-before-green enforced
      </div>
    </aside>
  );
}
