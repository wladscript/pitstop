import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Car, PlusCircle, Receipt, Star } from "lucide-react";

const items = [
    { to: "/garagem", icon: Car, label: "Garagem", testid: "nav-garage" },
    { to: "/novo-pedido", icon: PlusCircle, label: "Pedido", testid: "nav-new-order" },
    { to: "/pedidos", icon: Receipt, label: "Pedidos", testid: "nav-orders" },
    { to: "/fidelidade", icon: Star, label: "Pontos", testid: "nav-loyalty" },
];

export default function BottomNav() {
    const loc = useLocation();
    return (
        <nav
            data-testid="client-bottom-nav"
            className="fixed bottom-0 inset-x-0 z-40 border-t border-white/10 bg-black/70 backdrop-blur-xl"
        >
            <div className="max-w-md mx-auto grid grid-cols-4">
                {items.map(({ to, icon: Icon, label, testid }) => {
                    const active = loc.pathname.startsWith(to);
                    return (
                        <Link
                            key={to}
                            to={to}
                            data-testid={testid}
                            className={`flex flex-col items-center gap-1 py-3 text-[11px] uppercase tracking-widest transition-colors ${
                                active ? "text-white" : "text-white/50 hover:text-white/80"
                            }`}
                        >
                            <Icon size={20} strokeWidth={active ? 2.5 : 1.8} />
                            <span>{label}</span>
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}
