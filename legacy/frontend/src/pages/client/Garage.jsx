import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, Car, ChevronRight, LogOut, Star } from "lucide-react";
import { api, formatApiError } from "../../lib/api";
import { useAuth } from "../../lib/auth";
import BottomNav from "../../components/client/BottomNav";
import { toast } from "sonner";

export default function Garage() {
    const { user, logout } = useAuth();
    const nav = useNavigate();
    const [veiculos, setVeiculos] = useState([]);
    const [showAdd, setShowAdd] = useState(false);
    const [placa, setPlaca] = useState("");
    const [modelo, setModelo] = useState("");
    const [cor, setCor] = useState("");
    const [ano, setAno] = useState(2022);
    const [categoria, setCategoria] = useState("Médio");
    const [consulting, setConsulting] = useState(false);

    const load = async () => {
        const { data } = await api.get("/veiculos");
        setVeiculos(data);
    };

    useEffect(() => {
        load();
    }, []);

    const consultarPlaca = async () => {
        if (!placa) return;
        setConsulting(true);
        try {
            const { data } = await api.get(`/veiculos/consulta-placa/${placa}`);
            setModelo(data.modelo);
            setCor(data.cor);
            setAno(data.ano);
            setCategoria(data.categoria);
            toast.success("Dados preenchidos pela consulta");
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        } finally {
            setConsulting(false);
        }
    };

    const addVeiculo = async () => {
        try {
            await api.post("/veiculos", { placa, modelo, cor, ano: parseInt(ano), categoria });
            setShowAdd(false);
            setPlaca("");
            setModelo("");
            setCor("");
            toast.success("Veículo adicionado");
            load();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] noise pb-24">
            <div className="max-w-md mx-auto px-6 pt-8 relative z-10">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="text-xs uppercase tracking-widest text-white/40">
                            Olá,
                        </div>
                        <h1 className="font-display text-3xl uppercase tracking-tighter mt-1">
                            {user?.nome?.split(" ")[0]}
                        </h1>
                    </div>
                    <button
                        onClick={() => {
                            logout();
                            nav("/login");
                        }}
                        data-testid="client-logout-btn"
                        className="w-9 h-9 rounded-full border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                    >
                        <LogOut size={16} />
                    </button>
                </div>

                <div className="mt-6 rounded-2xl border border-[#FFD700]/20 bg-gradient-to-br from-[#FFD700]/5 to-transparent p-5 flex items-center gap-4">
                    <div className="w-11 h-11 rounded-full bg-[#FFD700]/10 flex items-center justify-center">
                        <Star size={20} className="text-[#FFD700]" />
                    </div>
                    <div className="flex-1">
                        <div className="text-xs uppercase tracking-widest text-white/50">
                            Pontos de fidelidade
                        </div>
                        <div className="font-display text-2xl text-[#FFD700]">
                            {user?.pontos_fidelidade ?? 0}
                        </div>
                    </div>
                    <Link
                        to="/fidelidade"
                        className="text-xs text-white/60 hover:text-white"
                        data-testid="loyalty-see-more"
                    >
                        Ver →
                    </Link>
                </div>

                <div className="flex items-center justify-between mt-10 mb-4">
                    <h2 className="font-display text-lg uppercase tracking-wide">
                        Minha Garagem
                    </h2>
                    <button
                        onClick={() => setShowAdd(!showAdd)}
                        data-testid="toggle-add-vehicle-btn"
                        className="flex items-center gap-1 text-sm text-[#3385FF]"
                    >
                        <Plus size={16} /> Adicionar
                    </button>
                </div>

                {showAdd && (
                    <div
                        data-testid="add-vehicle-form"
                        className="mb-6 p-4 rounded-xl bg-[#141414] border border-white/10 space-y-3"
                    >
                        <div className="flex gap-2">
                            <input
                                data-testid="vehicle-plate-input"
                                value={placa}
                                onChange={(e) => setPlaca(e.target.value.toUpperCase())}
                                placeholder="Placa (ABC1D23)"
                                className="flex-1 bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                            />
                            <button
                                onClick={consultarPlaca}
                                disabled={consulting}
                                data-testid="consult-plate-btn"
                                className="px-3 py-2 bg-white/5 border border-white/10 rounded text-xs uppercase tracking-widest hover:bg-white/10 transition-colors disabled:opacity-50"
                            >
                                {consulting ? "..." : "Consultar"}
                            </button>
                        </div>
                        <input
                            data-testid="vehicle-model-input"
                            value={modelo}
                            onChange={(e) => setModelo(e.target.value)}
                            placeholder="Modelo"
                            className="w-full bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                        />
                        <div className="grid grid-cols-2 gap-2">
                            <input
                                data-testid="vehicle-color-input"
                                value={cor}
                                onChange={(e) => setCor(e.target.value)}
                                placeholder="Cor"
                                className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                            />
                            <input
                                data-testid="vehicle-year-input"
                                type="number"
                                value={ano}
                                onChange={(e) => setAno(e.target.value)}
                                placeholder="Ano"
                                className="bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                            />
                        </div>
                        <select
                            data-testid="vehicle-category-select"
                            value={categoria}
                            onChange={(e) => setCategoria(e.target.value)}
                            className="w-full bg-[#1f1f1f] border border-white/10 rounded px-3 py-2 text-sm"
                        >
                            <option>Pequeno</option>
                            <option>Médio</option>
                            <option>Grande</option>
                        </select>
                        <button
                            onClick={addVeiculo}
                            data-testid="save-vehicle-btn"
                            className="w-full py-2 bg-[#0066FF] hover:bg-[#3385FF] rounded font-semibold text-sm uppercase tracking-widest transition-colors"
                        >
                            Salvar
                        </button>
                    </div>
                )}

                {veiculos.length === 0 ? (
                    <div className="text-center text-white/50 py-10 border border-dashed border-white/10 rounded-xl">
                        <Car className="mx-auto mb-2 opacity-50" />
                        Nenhum veículo cadastrado
                    </div>
                ) : (
                    <div className="space-y-3">
                        {veiculos.map((v) => (
                            <div
                                key={v.id}
                                data-testid={`vehicle-card-${v.placa}`}
                                className="relative rounded-xl overflow-hidden border border-white/10 bg-[#141414] p-4 flex items-center gap-4 hover:border-white/20 transition-colors"
                            >
                                <div className="w-14 h-14 rounded-lg bg-cover bg-center" style={{
                                    backgroundImage: "url(https://images.unsplash.com/photo-1596125099792-3917bf2d8095?crop=entropy&cs=srgb&fm=jpg&w=200&q=70)",
                                }} />
                                <div className="flex-1 min-w-0">
                                    <div className="font-semibold truncate">{v.modelo}</div>
                                    <div className="text-xs text-white/50">
                                        {v.placa} · {v.cor} · {v.ano}
                                    </div>
                                    <div className="mt-1 inline-block text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-white/70">
                                        {v.categoria}
                                    </div>
                                </div>
                                <ChevronRight size={18} className="text-white/30" />
                            </div>
                        ))}
                    </div>
                )}

                <Link
                    to="/novo-pedido"
                    data-testid="create-order-cta"
                    className="block mt-8 w-full py-4 rounded-full bg-[#0066FF] hover:bg-[#3385FF] text-center font-semibold uppercase tracking-widest text-sm transition-colors"
                >
                    Novo Pedido de Lavagem
                </Link>
            </div>
            <BottomNav />
        </div>
    );
}
