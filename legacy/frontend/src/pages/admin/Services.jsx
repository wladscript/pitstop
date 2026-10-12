import React, { useEffect, useState } from "react";
import { api, formatApiError } from "../../lib/api";
import Sidebar from "../../components/admin/Sidebar";
import { toast } from "sonner";

export default function Services() {
    const [servicos, setServicos] = useState([]);
    const [nome, setNome] = useState("");
    const [descricao, setDescricao] = useState("");
    const [preco, setPreco] = useState("");

    const load = () => api.get("/servicos").then((r) => setServicos(r.data));
    useEffect(() => {
        load();
    }, []);

    const create = async () => {
        if (!nome || !preco) return;
        try {
            await api.post("/servicos", {
                nome,
                descricao,
                preco_base: parseFloat(preco),
            });
            setNome("");
            setDescricao("");
            setPreco("");
            toast.success("Serviço criado");
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-8">
                <h1 className="font-display text-2xl uppercase tracking-tight">Serviços</h1>
                <p className="text-sm text-white/50 mt-1">
                    Catálogo precificado (multiplicador por categoria aplicado automaticamente).
                </p>

                <div className="mt-6 p-5 rounded-lg bg-[#141414] border border-white/10 grid grid-cols-4 gap-3">
                    <input
                        data-testid="service-name-input"
                        value={nome}
                        onChange={(e) => setNome(e.target.value)}
                        placeholder="Nome"
                        className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                    />
                    <input
                        data-testid="service-desc-input"
                        value={descricao}
                        onChange={(e) => setDescricao(e.target.value)}
                        placeholder="Descrição"
                        className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm col-span-2"
                    />
                    <input
                        data-testid="service-price-input"
                        type="number"
                        step="0.01"
                        value={preco}
                        onChange={(e) => setPreco(e.target.value)}
                        placeholder="Preço base"
                        className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                    />
                    <button
                        onClick={create}
                        data-testid="service-create-btn"
                        className="col-span-4 bg-[#0066FF] hover:bg-[#3385FF] rounded py-2 text-xs uppercase tracking-widest font-semibold transition-colors"
                    >
                        Criar serviço
                    </button>
                </div>

                <div className="mt-6 space-y-2">
                    {servicos.map((s) => (
                        <div
                            key={s.id}
                            data-testid={`service-row-${s.id}`}
                            className="p-4 rounded-lg bg-[#141414] border border-white/10 flex items-center justify-between"
                        >
                            <div>
                                <div className="font-semibold">{s.nome}</div>
                                <div className="text-xs text-white/50">{s.descricao}</div>
                            </div>
                            <div className="font-display text-xl">R$ {s.preco_base.toFixed(2)}</div>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
