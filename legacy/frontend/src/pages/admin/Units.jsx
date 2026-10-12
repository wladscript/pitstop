import React, { useEffect, useState } from "react";
import { api, formatApiError } from "../../lib/api";
import Sidebar from "../../components/admin/Sidebar";
import { toast } from "sonner";

export default function Units() {
    const [units, setUnits] = useState([]);
    const [nome, setNome] = useState("");
    const [endereco, setEndereco] = useState("");

    const load = () => api.get("/unidades/status").then((r) => setUnits(r.data));
    useEffect(() => {
        load();
    }, []);

    const toggle = async (u) => {
        try {
            await api.patch(`/unidades/${u.id}`, {
                nome: u.nome,
                endereco: u.endereco,
                is_ativa: !u.is_ativa,
            });
            toast.success(u.is_ativa ? "Kill-switch ativado" : "Unidade reativada");
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    const create = async () => {
        if (!nome || !endereco) return;
        try {
            await api.post("/unidades", { nome, endereco, is_ativa: true });
            setNome("");
            setEndereco("");
            toast.success("Unidade criada");
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-8">
                <h1 className="font-display text-2xl uppercase tracking-tight">Unidades</h1>
                <p className="text-sm text-white/50 mt-1">
                    Controle de operação e kill-switch de lotação.
                </p>

                <div className="mt-6 p-5 rounded-lg bg-[#141414] border border-white/10 grid grid-cols-3 gap-3">
                    <input
                        data-testid="unit-name-input"
                        value={nome}
                        onChange={(e) => setNome(e.target.value)}
                        placeholder="Nome da unidade"
                        className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                    />
                    <input
                        data-testid="unit-address-input"
                        value={endereco}
                        onChange={(e) => setEndereco(e.target.value)}
                        placeholder="Endereço"
                        className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                    />
                    <button
                        onClick={create}
                        data-testid="unit-create-btn"
                        className="bg-[#0066FF] hover:bg-[#3385FF] rounded text-xs uppercase tracking-widest font-semibold transition-colors"
                    >
                        Criar unidade
                    </button>
                </div>

                <div className="mt-6 space-y-2">
                    {units.map((u) => (
                        <div
                            key={u.id}
                            data-testid={`unit-row-${u.id}`}
                            className="p-4 rounded-lg bg-[#141414] border border-white/10 flex items-center justify-between"
                        >
                            <div>
                                <div className="font-semibold">{u.nome}</div>
                                <div className="text-xs text-white/50">{u.endereco}</div>
                                <div className="text-xs text-white/40 mt-1">
                                    {u.ordens_ativas} ordens ativas
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <span
                                    className={`text-xs uppercase tracking-widest px-2 py-1 rounded ${
                                        u.is_ativa
                                            ? "bg-emerald-500/15 text-emerald-400"
                                            : "bg-red-500/15 text-red-400"
                                    }`}
                                >
                                    {u.is_ativa ? "Operando" : "Lotada"}
                                </span>
                                <button
                                    onClick={() => toggle(u)}
                                    data-testid={`toggle-unit-${u.id}`}
                                    className="px-4 py-2 rounded border border-white/10 text-xs uppercase tracking-widest hover:bg-white/5 transition-colors"
                                >
                                    {u.is_ativa ? "Ativar Kill-switch" : "Reativar"}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
