import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { api } from "../../lib/api";
import BottomNav from "../../components/client/BottomNav";

const STATUS_FLOW = ["Na Fila", "Preparação", "Execução", "Pronto", "Finalizado"];

export default function OrderDetail() {
    const { id } = useParams();
    const nav = useNavigate();
    const [os, setOs] = useState(null);

    const load = () => api.get(`/ordens-servico/${id}`).then((r) => setOs(r.data));

    useEffect(() => {
        load();
        const t = setInterval(load, 7000);
        return () => clearInterval(t);
    }, [id]);

    if (!os) return <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center text-white/60">Carregando…</div>;

    const stepIdx = STATUS_FLOW.indexOf(os.status);

    return (
        <div className="min-h-screen bg-[#0a0a0a] pb-28">
            <div className="max-w-md mx-auto px-6 pt-6">
                <button onClick={() => nav(-1)} data-testid="back-btn" className="flex items-center text-white/60 text-sm">
                    <ChevronLeft size={18} /> Voltar
                </button>

                <div className="mt-4">
                    <div className="text-xs uppercase tracking-widest text-white/40">Pedido</div>
                    <h1 className="font-display text-3xl uppercase tracking-tighter">
                        {os.veiculo?.modelo}
                    </h1>
                    <div className="text-sm text-white/50">{os.veiculo?.placa} · {os.unidade?.nome}</div>
                </div>

                <div className="mt-8">
                    <div className="text-xs uppercase tracking-widest text-white/50 mb-3">Status</div>
                    <div className="space-y-3">
                        {STATUS_FLOW.map((s, i) => (
                            <div key={s} className="flex items-center gap-3">
                                <div
                                    className={`w-4 h-4 rounded-full border-2 ${
                                        i < stepIdx
                                            ? "bg-[#34D399] border-[#34D399]"
                                            : i === stepIdx
                                            ? "bg-[#0066FF] border-[#0066FF] animate-pulse"
                                            : "border-white/20"
                                    }`}
                                />
                                <span className={`text-sm ${i <= stepIdx ? "text-white" : "text-white/40"}`}>
                                    {s}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="mt-8 p-4 rounded-xl bg-[#141414] border border-white/10">
                    <div className="text-xs uppercase tracking-widest text-white/50">Serviços</div>
                    <ul className="mt-2 space-y-1 text-sm">
                        {os.servicos?.map((s) => (
                            <li key={s.id} className="flex justify-between">
                                <span className="text-white/80">{s.nome}</span>
                                <span className="text-white/50">R$ {s.preco_base.toFixed(2)}</span>
                            </li>
                        ))}
                    </ul>
                    <div className="border-t border-white/10 mt-3 pt-3 flex justify-between">
                        <span className="text-xs uppercase tracking-widest text-white/50">Total</span>
                        <span className="font-display text-xl">R$ {os.valor_total.toFixed(2)}</span>
                    </div>
                </div>

                <div className="mt-6 p-4 rounded-xl bg-[#141414] border border-white/10">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="text-xs uppercase tracking-widest text-white/50">Pagamento</div>
                            <div className={`mt-1 font-semibold ${os.status_pagamento === "Pago" ? "text-[#34D399]" : "text-[#FBBF24]"}`}>
                                {os.status_pagamento}
                            </div>
                        </div>
                        {os.status_pagamento === "Pendente" && (
                            <Link
                                to={`/pedidos/${os.id}/pix`}
                                data-testid="pay-pix-btn"
                                className="px-5 py-2.5 rounded-full bg-[#FFD700] text-black font-bold uppercase text-xs tracking-widest hover:brightness-110 transition-all"
                            >
                                Pagar com Pix
                            </Link>
                        )}
                    </div>
                </div>
            </div>
            <BottomNav />
        </div>
    );
}
