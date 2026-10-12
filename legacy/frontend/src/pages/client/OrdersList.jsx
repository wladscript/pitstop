import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import BottomNav from "../../components/client/BottomNav";

const STATUS_CLASS = {
    "Na Fila": "status-nafila",
    "Preparação": "status-preparacao",
    "Execução": "status-execucao",
    "Pronto": "status-pronto",
    "Finalizado": "status-finalizado",
};

export default function OrdersList() {
    const [ordens, setOrdens] = useState([]);

    useEffect(() => {
        api.get("/ordens-servico").then((r) => setOrdens(r.data));
    }, []);

    return (
        <div className="min-h-screen bg-[#0a0a0a] pb-24">
            <div className="max-w-md mx-auto px-6 pt-8">
                <h1 className="font-display text-3xl uppercase tracking-tighter">Meus Pedidos</h1>
                <p className="text-sm text-white/50 mt-1">Acompanhe o status em tempo real.</p>

                <div className="mt-6 space-y-3">
                    {ordens.length === 0 && (
                        <div className="text-center text-white/50 py-10 border border-dashed border-white/10 rounded-xl">
                            Nenhum pedido ainda
                        </div>
                    )}
                    {ordens.map((o) => (
                        <Link
                            key={o.id}
                            to={`/pedidos/${o.id}`}
                            data-testid={`order-card-${o.id}`}
                            className="block p-4 rounded-xl bg-[#141414] border border-white/10 hover:border-white/20 transition-colors"
                        >
                            <div className="flex items-start justify-between">
                                <div className="min-w-0">
                                    <div className="font-semibold truncate">
                                        {o.veiculo?.modelo} · {o.veiculo?.placa}
                                    </div>
                                    <div className="text-xs text-white/50 truncate">
                                        {o.unidade?.nome}
                                    </div>
                                </div>
                                <span
                                    className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded-full ${STATUS_CLASS[o.status]}`}
                                >
                                    {o.status}
                                </span>
                            </div>
                            <div className="mt-3 flex items-center justify-between text-sm">
                                <span className="text-white/60">
                                    {o.status_pagamento === "Pago" ? "✓ Pago" : "Pagamento pendente"}
                                </span>
                                <span className="font-display text-lg">R$ {o.valor_total.toFixed(2)}</span>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
            <BottomNav />
        </div>
    );
}
