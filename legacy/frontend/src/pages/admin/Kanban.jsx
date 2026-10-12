import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "../../lib/api";
import Sidebar from "../../components/admin/Sidebar";
import { toast } from "sonner";

const COLUMNS = [
    { key: "Na Fila", color: "#64748B" },
    { key: "Preparação", color: "#F59E0B" },
    { key: "Execução", color: "#3B82F6" },
    { key: "Pronto", color: "#10B981" },
    { key: "Finalizado", color: "#22C55E" },
];

export default function Kanban() {
    const [ordens, setOrdens] = useState([]);
    const [dragging, setDragging] = useState(null);

    const load = () => api.get("/ordens-servico").then((r) => setOrdens(r.data));

    useEffect(() => {
        load();
        const t = setInterval(load, 10000);
        return () => clearInterval(t);
    }, []);

    const moverStatus = async (id, status) => {
        try {
            await api.patch(`/ordens-servico/${id}/status`, { status });
            toast.success(`Status: ${status}`);
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 flex flex-col">
                <header className="px-8 py-5 border-b border-white/10 flex items-center justify-between">
                    <div>
                        <h1 className="font-display text-2xl uppercase tracking-tight">Kanban Operacional</h1>
                        <p className="text-xs text-white/50 mt-1">Arraste cartões para mover o status</p>
                    </div>
                    <div className="flex gap-6">
                        {COLUMNS.map((c) => {
                            const n = ordens.filter((o) => o.status === c.key).length;
                            return (
                                <div key={c.key} className="text-center">
                                    <div className="text-[10px] uppercase tracking-widest text-white/40">
                                        {c.key}
                                    </div>
                                    <div className="font-display text-xl" style={{ color: c.color }}>
                                        {n}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </header>

                <div className="flex-1 p-6 grid grid-cols-5 gap-4 overflow-hidden">
                    {COLUMNS.map((c) => (
                        <div
                            key={c.key}
                            data-testid={`kanban-column-${c.key}`}
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={(e) => {
                                e.preventDefault();
                                if (dragging && dragging.status !== c.key)
                                    moverStatus(dragging.id, c.key);
                                setDragging(null);
                            }}
                            className="flex flex-col rounded-lg border border-white/10 bg-[#111]"
                        >
                            <div
                                className="px-4 py-3 border-b border-white/10 flex items-center justify-between"
                                style={{ borderTop: `3px solid ${c.color}` }}
                            >
                                <div className="text-xs uppercase tracking-widest font-semibold">
                                    {c.key}
                                </div>
                                <div className="text-xs text-white/40">
                                    {ordens.filter((o) => o.status === c.key).length}
                                </div>
                            </div>
                            <div className="flex-1 p-2 space-y-2 overflow-auto kanban-col">
                                {ordens
                                    .filter((o) => o.status === c.key)
                                    .map((o) => (
                                        <div
                                            key={o.id}
                                            draggable
                                            onDragStart={() => setDragging(o)}
                                            data-testid={`kanban-card-${o.id}`}
                                            className="p-3 rounded-md bg-[#1a1a1a] border border-white/10 cursor-grab active:cursor-grabbing hover:border-white/25 transition-colors"
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="text-xs text-white/50">
                                                    #{o.id.slice(0, 6)}
                                                </div>
                                                <div
                                                    className={`text-[10px] px-1.5 py-0.5 rounded ${
                                                        o.status_pagamento === "Pago"
                                                            ? "bg-emerald-500/15 text-emerald-400"
                                                            : "bg-amber-500/15 text-amber-400"
                                                    }`}
                                                >
                                                    {o.status_pagamento}
                                                </div>
                                            </div>
                                            <div className="mt-1 font-semibold text-sm truncate">
                                                {o.veiculo?.modelo}
                                            </div>
                                            <div className="text-xs text-white/50">
                                                {o.veiculo?.placa} · {o.cliente?.nome}
                                            </div>
                                            <div className="mt-2 flex items-center justify-between">
                                                <span className="text-sm font-display">
                                                    R$ {o.valor_total.toFixed(2)}
                                                </span>
                                                <Link
                                                    to={`/admin/os/${o.id}`}
                                                    data-testid={`open-os-${o.id}`}
                                                    className="text-[10px] uppercase tracking-widest text-[#3385FF] hover:underline"
                                                >
                                                    Abrir
                                                </Link>
                                            </div>
                                        </div>
                                    ))}
                            </div>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
