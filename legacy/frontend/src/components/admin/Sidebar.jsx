import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LayoutGrid, Building2, Wrench, Users, LogOut, Zap } from "lucide-react";
import { useAuth } from "../../lib/auth";

const items = [
    { to: "/admin", icon: LayoutGrid, label: "Kanban", testid: "admin-nav-kanban" },
    { to: "/admin/unidades", icon: Building2, label: "Unidades", testid: "admin-nav-units" },
    { to: "/admin/servicos", icon: Wrench, label: "Serviços", testid: "admin-nav-services" },
    { to: "/admin/clientes", icon: Users, label: "Clientes", testid: "admin-nav-clients" },
];

export default function Sidebar() {
    const loc = useLocation();
    const nav = useNavigate();
    const { user, logout } = useAuth();

    return (
        <aside className="w-60 shrink-0 h-screen sticky top-0 border-r border-white/10 bg-[#0f0f10] flex flex-col">
            <div className="px-5 py-6 border-b border-white/10">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-md bg-[#0066FF] flex items-center justify-center">
                        <Zap size={18} className="text-white" />
                    </div>
                    <div>
                        <div className="font-display text-lg uppercase tracking-wide">
                            Pit Stop
                        </div>
                        <div className="text-[10px] uppercase tracking-widest text-white/40">
                            Admin
                        </div>
                    </div>
                </div>
            </div>
            <nav className="flex-1 py-4">
                {items.map(({ to, icon: Icon, label, testid }) => {
                    const active = loc.pathname === to || (to !== "/admin" && loc.pathname.startsWith(to));
                    return (
                        <Link
                            key={to}
                            to={to}
                            data-testid={testid}
                            className={`flex items-center gap-3 px-5 py-3 text-sm transition-colors ${
                                active
                                    ? "bg-white/5 text-white border-l-2 border-[#0066FF]"
                                    : "text-white/55 hover:text-white hover:bg-white/[0.03]"
                            }`}
                        >
                            <Icon size={16} />
                            <span>{label}</span>
                        </Link>
                    );
                })}
            </nav>
            <div className="px-5 py-4 border-t border-white/10">
                <div className="text-[11px] uppercase tracking-widest text-white/40 mb-1">
                    Logado como
                </div>
                <div className="text-sm text-white/90">{user?.nome}</div>
                <button
                    data-testid="admin-logout-btn"
                    onClick={() => {
                        logout();
                        nav("/login");
                    }}
                    className="mt-3 w-full flex items-center justify-center gap-2 py-2 text-xs uppercase tracking-widest text-white/70 border border-white/10 rounded hover:bg-white/5 transition-colors"
                >
                    <LogOut size={14} /> Sair
                </button>
            </div>
        </aside>
    );
}
