import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronLeft, Check } from "lucide-react";
import { api, formatApiError } from "../../lib/api";
import BottomNav from "../../components/client/BottomNav";
import { toast } from "sonner";

export default function NewOrder() {
    const nav = useNavigate();
    const [step, setStep] = useState(1);
    const [veiculos, setVeiculos] = useState([]);
    const [unidades, setUnidades] = useState([]);
    const [servicos, setServicos] = useState([]);

    const [veiculoId, setVeiculoId] = useState("");
    const [unidadeId, setUnidadeId] = useState("");
    const [servicoIds, setServicoIds] = useState([]);
    const [logEntrada, setLogEntrada] = useState("Entrega no local");
    const [logSaida, setLogSaida] = useState("Retirada no local");
    const [enderecos, setEnderecos] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        api.get("/veiculos").then((r) => setVeiculos(r.data));
        api.get("/unidades/status").then((r) => setUnidades(r.data));
        api.get("/servicos").then((r) => setServicos(r.data));
    }, []);

    const toggleServ = (id) =>
        setServicoIds((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]));

    const veiculo = veiculos.find((v) => v.id === veiculoId);
    const mult = veiculo?.categoria === "Grande" ? 1.6 : veiculo?.categoria === "Médio" ? 1.3 : 1.0;
    const total = servicoIds.reduce((acc, id) => {
        const s = servicos.find((x) => x.id === id);
        return acc + (s?.preco_base || 0);
    }, 0) * mult;

    const criar = async () => {
        setSubmitting(true);
        try {
            const { data } = await api.post("/ordens-servico", {
                veiculo_id: veiculoId,
                unidade_id: unidadeId,
                servico_ids: servicoIds,
                logistica_entrada: logEntrada,
                logistica_saida: logSaida,
                enderecos,
            });
            toast.success("Pedido criado!");
            nav(`/pedidos/${data.id}`);
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        } finally {
            setSubmitting(false);
        }
    };

    const canNext =
        (step === 1 && veiculoId) ||
        (step === 2 && unidadeId) ||
        (step === 3 && servicoIds.length > 0);

    return (
        <div className="min-h-screen bg-[#0a0a0a] pb-28">
            <div className="max-w-md mx-auto px-6 pt-6">
                <button
                    onClick={() => (step > 1 ? setStep(step - 1) : nav(-1))}
                    data-testid="back-btn"
                    className="flex items-center text-white/60 text-sm"
                >
                    <ChevronLeft size={18} /> Voltar
                </button>
                <h1 className="font-display text-3xl uppercase tracking-tighter mt-4">
                    Novo pedido
                </h1>
                <div className="text-xs uppercase tracking-widest text-white/40 mt-1">
                    Passo {step} de 4
                </div>

                <div className="flex gap-1 mt-4">
                    {[1, 2, 3, 4].map((n) => (
                        <div
                            key={n}
                            className={`h-1 flex-1 rounded ${n <= step ? "bg-[#0066FF]" : "bg-white/10"}`}
                        />
                    ))}
                </div>

                {step === 1 && (
                    <div className="mt-6 space-y-3" data-testid="step-vehicle">
                        <h2 className="font-display text-lg uppercase tracking-wide">Veículo</h2>
                        {veiculos.map((v) => (
                            <button
                                key={v.id}
                                onClick={() => setVeiculoId(v.id)}
                                data-testid={`pick-vehicle-${v.placa}`}
                                className={`w-full text-left p-4 rounded-xl border transition-colors ${
                                    veiculoId === v.id
                                        ? "border-[#0066FF] bg-[#0066FF]/5"
                                        : "border-white/10 bg-[#141414] hover:border-white/20"
                                }`}
                            >
                                <div className="font-semibold">{v.modelo}</div>
                                <div className="text-xs text-white/50">
                                    {v.placa} · {v.categoria}
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {step === 2 && (
                    <div className="mt-6 space-y-3" data-testid="step-unit">
                        <h2 className="font-display text-lg uppercase tracking-wide">Unidade</h2>
                        {unidades.map((u) => (
                            <button
                                key={u.id}
                                onClick={() => u.disponivel && setUnidadeId(u.id)}
                                disabled={!u.disponivel}
                                data-testid={`pick-unit-${u.id}`}
                                className={`w-full text-left p-4 rounded-xl border transition-colors ${
                                    !u.disponivel
                                        ? "border-red-500/20 bg-red-500/5 opacity-60 cursor-not-allowed"
                                        : unidadeId === u.id
                                        ? "border-[#0066FF] bg-[#0066FF]/5"
                                        : "border-white/10 bg-[#141414] hover:border-white/20"
                                }`}
                            >
                                <div className="font-semibold">{u.nome}</div>
                                <div className="text-xs text-white/50">{u.endereco}</div>
                                <div className="mt-2 text-xs">
                                    {u.disponivel ? (
                                        <span className="text-[#34D399]">
                                            Disponível · {u.ordens_ativas} na fila
                                        </span>
                                    ) : (
                                        <span className="text-red-400">
                                            Lotação máxima
                                        </span>
                                    )}
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {step === 3 && (
                    <div className="mt-6 space-y-3" data-testid="step-services">
                        <h2 className="font-display text-lg uppercase tracking-wide">Serviços</h2>
                        <p className="text-xs text-white/50">
                            Categoria {veiculo?.categoria} aplica multiplicador ×{mult}
                        </p>
                        {servicos.map((s) => (
                            <button
                                key={s.id}
                                onClick={() => toggleServ(s.id)}
                                data-testid={`pick-service-${s.id}`}
                                className={`w-full text-left p-4 rounded-xl border transition-colors flex items-center gap-3 ${
                                    servicoIds.includes(s.id)
                                        ? "border-[#0066FF] bg-[#0066FF]/5"
                                        : "border-white/10 bg-[#141414] hover:border-white/20"
                                }`}
                            >
                                <div
                                    className={`w-5 h-5 rounded border flex items-center justify-center ${
                                        servicoIds.includes(s.id)
                                            ? "bg-[#0066FF] border-[#0066FF]"
                                            : "border-white/30"
                                    }`}
                                >
                                    {servicoIds.includes(s.id) && <Check size={12} />}
                                </div>
                                <div className="flex-1">
                                    <div className="font-semibold">{s.nome}</div>
                                    <div className="text-xs text-white/50">{s.descricao}</div>
                                </div>
                                <div className="text-sm text-white/80">
                                    R$ {s.preco_base.toFixed(2)}
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {step === 4 && (
                    <div className="mt-6 space-y-4" data-testid="step-review">
                        <h2 className="font-display text-lg uppercase tracking-wide">Logística</h2>
                        <div>
                            <label className="text-xs uppercase tracking-widest text-white/50">Entrada</label>
                            <input
                                data-testid="log-entrada-input"
                                value={logEntrada}
                                onChange={(e) => setLogEntrada(e.target.value)}
                                className="mt-1 w-full bg-[#141414] border border-white/10 rounded px-3 py-2"
                            />
                        </div>
                        <div>
                            <label className="text-xs uppercase tracking-widest text-white/50">Saída</label>
                            <input
                                data-testid="log-saida-input"
                                value={logSaida}
                                onChange={(e) => setLogSaida(e.target.value)}
                                className="mt-1 w-full bg-[#141414] border border-white/10 rounded px-3 py-2"
                            />
                        </div>
                        <div>
                            <label className="text-xs uppercase tracking-widest text-white/50">
                                Endereço (opcional)
                            </label>
                            <textarea
                                data-testid="enderecos-input"
                                value={enderecos}
                                onChange={(e) => setEnderecos(e.target.value)}
                                className="mt-1 w-full bg-[#141414] border border-white/10 rounded px-3 py-2 h-20"
                            />
                        </div>

                        <div className="mt-6 p-4 rounded-xl bg-gradient-to-br from-[#0066FF]/10 to-transparent border border-[#0066FF]/30">
                            <div className="text-xs uppercase tracking-widest text-white/50">Total</div>
                            <div className="font-display text-4xl text-white">
                                R$ {total.toFixed(2)}
                            </div>
                        </div>
                    </div>
                )}

                <div className="mt-8">
                    {step < 4 ? (
                        <button
                            onClick={() => canNext && setStep(step + 1)}
                            data-testid="next-step-btn"
                            disabled={!canNext}
                            className="w-full py-3 rounded-full bg-[#0066FF] hover:bg-[#3385FF] font-semibold uppercase tracking-widest text-sm disabled:opacity-40 transition-colors"
                        >
                            Avançar
                        </button>
                    ) : (
                        <button
                            onClick={criar}
                            disabled={submitting}
                            data-testid="confirm-order-btn"
                            className="w-full py-3 rounded-full bg-[#FFD700] hover:brightness-110 text-black font-bold uppercase tracking-widest text-sm transition-all disabled:opacity-50"
                        >
                            {submitting ? "Criando…" : "Confirmar pedido"}
                        </button>
                    )}
                </div>
            </div>
            <BottomNav />
        </div>
    );
}
