import React from "react";
import { Star } from "lucide-react";
import { useAuth } from "../../lib/auth";
import BottomNav from "../../components/client/BottomNav";

export default function Loyalty() {
    const { user } = useAuth();
    const pts = user?.pontos_fidelidade ?? 0;
    const nextTier = pts < 100 ? 100 : pts < 300 ? 300 : pts < 600 ? 600 : 1000;
    const pct = Math.min(100, (pts / nextTier) * 100);

    return (
        <div className="min-h-screen bg-[#0a0a0a] pb-28">
            <div className="max-w-md mx-auto px-6 pt-8">
                <h1 className="font-display text-3xl uppercase tracking-tighter">Fidelidade</h1>
                <p className="text-sm text-white/50 mt-1">Ganhe pontos a cada lavagem finalizada.</p>

                <div className="mt-6 p-6 rounded-2xl bg-gradient-to-br from-[#FFD700]/15 to-transparent border border-[#FFD700]/30">
                    <div className="flex items-center gap-3">
                        <Star className="text-[#FFD700]" />
                        <div className="text-xs uppercase tracking-widest text-white/60">Saldo</div>
                    </div>
                    <div className="font-display text-6xl text-[#FFD700] mt-2">{pts}</div>
                    <div className="text-xs text-white/50 mt-1">pontos</div>

                    <div className="mt-4">
                        <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-[#FFD700] transition-all"
                                style={{ width: `${pct}%` }}
                            />
                        </div>
                        <div className="text-xs text-white/50 mt-2">
                            Faltam {nextTier - pts} pts para o próximo nível
                        </div>
                    </div>
                </div>

                <div className="mt-8">
                    <h2 className="font-display text-lg uppercase tracking-wide mb-3">Como funciona</h2>
                    <div className="space-y-3 text-sm text-white/70">
                        <div className="p-4 rounded-xl bg-[#141414] border border-white/10">
                            Ganhe <b className="text-white">1 ponto a cada R$10</b> gastos em serviços finalizados.
                        </div>
                        <div className="p-4 rounded-xl bg-[#141414] border border-white/10">
                            Troque pontos por lavagens cortesia (em breve).
                        </div>
                    </div>
                </div>
            </div>
            <BottomNav />
        </div>
    );
}
