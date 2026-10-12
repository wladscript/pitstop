import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { api, formatApiError } from "../../lib/api";
import Sidebar from "../../components/admin/Sidebar";
import { toast } from "sonner";

const STATUS = ["Na Fila", "Preparação", "Execução", "Pronto", "Finalizado"];

export default function OrderDetailAdmin() {
    const { id } = useParams();
    const nav = useNavigate();
    const [os, setOs] = useState(null);
    const [newPrice, setNewPrice] = useState("");

    const load = () => api.get(`/ordens-servico/${id}`).then((r) => setOs(r.data));

    useEffect(() => {
        load();
    }, [id]);

    const changeStatus = async (status) => {
        try {
            await api.patch(`/ordens-servico/${id}/status`, { status });
            toast.success(`Status: ${status}`);
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    const overridePrice = async () => {
        if (!newPrice) return;
        try {
            await api.patch(`/ordens-servico/${id}/preco`, { valor_total: parseFloat(newPrice) });
            toast.success("Valor atualizado");
            setNewPrice("");
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    const togglePagamento = async () => {
        try {
            const novoStatus = os.status_pagamento === "Pago" ? "Pendente" : "Pago";
            await api.patch(`/ordens-servico/${id}/pagamento`, { status_pagamento: novoStatus });
            toast.success(`Pagamento: ${novoStatus}`);
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    if (!os)
        return (
            <div className="flex min-h-screen">
                <Sidebar />
                <main className="flex-1 flex items-center justify-center text-white/60">
                    Carregando…
                </main>
            </div>
        );

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-8">
                <button
                    onClick={() => nav(-1)}
                    data-testid="back-btn"
                    className="flex items-center text-white/60 text-sm"
                >
                    <ChevronLeft size={18} /> Voltar
                </button>

                <div className="mt-4 flex items-start justify-between gap-6">
                    <div>
                        <div className="text-xs uppercase tracking-widest text-white/40">
                            OS #{os.id.slice(0, 8)}
                        </div>
                        <h1 className="font-display text-3xl uppercase tracking-tight">
                            {os.veiculo?.modelo}
                        </h1>
                        <div className="text-sm text-white/50 mt-1">
                            {os.veiculo?.placa} · {os.cliente?.nome} ({os.cliente?.telefone})
                        </div>
                    </div>
                    <div>
                        <div className="text-xs uppercase tracking-widest text-white/40">Valor</div>
                        <div className="font-display text-4xl">R$ {os.valor_total.toFixed(2)}</div>
                        {os.override_preco && (
                            <span className="text-[10px] uppercase tracking-widest text-[#FFD700]">
                                Preço sobrescrito
                            </span>
                        )}
                    </div>
                </div>

                <div className="mt-8 grid grid-cols-2 gap-6">
                    <section className="p-5 rounded-lg bg-[#141414] border border-white/10">
                        <div className="text-xs uppercase tracking-widest text-white/50 mb-3">
                            Mover status
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {STATUS.map((s) => (
                                <button
                                    key={s}
                                    onClick={() => changeStatus(s)}
                                    data-testid={`set-status-${s}`}
                                    className={`px-3 py-2 rounded-md text-xs uppercase tracking-widest border transition-colors ${
                                        os.status === s
                                            ? "bg-[#0066FF] border-[#0066FF] text-white"
                                            : "border-white/10 text-white/70 hover:bg-white/5"
                                    }`}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                        <p className="text-xs text-white/40 mt-3">
                            * Finalizado só é permitido com pagamento Pago.
                        </p>
                    </section>

                    <section className="p-5 rounded-lg bg-[#141414] border border-white/10">
                        <div className="text-xs uppercase tracking-widest text-white/50 mb-3">
                            Pagamento
                        </div>
                        <div
                            className={`inline-block px-3 py-1 rounded text-xs uppercase tracking-widest ${
                                os.status_pagamento === "Pago"
                                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                    : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                            }`}
                        >
                            {os.status_pagamento}
                        </div>
                        <button
                            onClick={togglePagamento}
                            data-testid="toggle-payment-btn"
                            className="block mt-3 px-4 py-2 rounded-md border border-white/10 text-xs uppercase tracking-widest hover:bg-white/5 transition-colors"
                        >
                            {os.status_pagamento === "Pago"
                                ? "Reverter para Pendente"
                                : "Confirmar como Pago"}
                        </button>
                    </section>

                    <section className="p-5 rounded-lg bg-[#141414] border border-white/10">
                        <div className="text-xs uppercase tracking-widest text-white/50 mb-3">
                            Override de preço
                        </div>
                        <div className="flex gap-2">
                            <input
                                data-testid="override-price-input"
                                type="number"
                                step="0.01"
                                value={newPrice}
                                onChange={(e) => setNewPrice(e.target.value)}
                                placeholder="Novo valor"
                                className="flex-1 bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                            />
                            <button
                                onClick={overridePrice}
                                data-testid="override-price-btn"
                                className="px-4 py-2 bg-[#0066FF] rounded-md text-xs uppercase tracking-widest font-semibold hover:bg-[#3385FF] transition-colors"
                            >
                                Aplicar
                            </button>
                        </div>
                    </section>

                    <section className="p-5 rounded-lg bg-[#141414] border border-white/10">
                        <div className="text-xs uppercase tracking-widest text-white/50 mb-3">
                            Serviços
                        </div>
                        <ul className="space-y-1 text-sm">
                            {os.servicos?.map((s) => (
                                <li key={s.id} className="flex justify-between">
                                    <span>{s.nome}</span>
                                    <span className="text-white/50">R$ {s.preco_base.toFixed(2)}</span>
                                </li>
                            ))}
                        </ul>
                        <div className="text-xs text-white/40 mt-3">
                            Logística: {os.logistica_entrada} → {os.logistica_saida}
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
}
