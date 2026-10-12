import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, Copy, Check } from "lucide-react";
import { api, formatApiError } from "../../lib/api";
import BottomNav from "../../components/client/BottomNav";
import { toast } from "sonner";

export default function Pix() {
    const { id } = useParams();
    const nav = useNavigate();
    const [pix, setPix] = useState(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        api.post("/pagamentos/pix", { ordem_id: id })
            .then((r) => setPix(r.data))
            .catch((e) => toast.error(formatApiError(e.response?.data?.detail)));
    }, [id]);

    const copy = async () => {
        await navigator.clipboard.writeText(pix.pix_copia_cola);
        setCopied(true);
        toast.success("Código copiado!");
        setTimeout(() => setCopied(false), 2500);
    };

    if (!pix) return <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center text-white/60">Gerando Pix…</div>;

    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=280x280&margin=10&data=${encodeURIComponent(pix.pix_copia_cola)}`;

    return (
        <div className="min-h-screen bg-[#0a0a0a] pb-28">
            <div className="max-w-md mx-auto px-6 pt-6">
                <button onClick={() => nav(-1)} data-testid="back-btn" className="flex items-center text-white/60 text-sm">
                    <ChevronLeft size={18} /> Voltar
                </button>

                <h1 className="font-display text-3xl uppercase tracking-tighter mt-4">
                    Pagar com Pix
                </h1>
                <p className="text-sm text-white/50 mt-1">
                    Escaneie o QR Code ou copie e cole o código.
                </p>

                <div className="mt-6 p-6 rounded-2xl bg-white flex items-center justify-center">
                    <img src={qrUrl} alt="QR Pix" className="w-64 h-64" data-testid="pix-qr-img" />
                </div>

                <div className="mt-4 p-4 rounded-xl bg-[#141414] border border-white/10">
                    <div className="text-xs uppercase tracking-widest text-white/50">Valor</div>
                    <div className="font-display text-3xl">R$ {pix.valor.toFixed(2)}</div>
                </div>

                <div className="mt-4 p-4 rounded-xl bg-[#141414] border border-white/10">
                    <div className="text-xs uppercase tracking-widest text-white/50 mb-2">Pix Copia e Cola</div>
                    <div
                        data-testid="pix-code"
                        className="text-[11px] text-white/70 break-all font-mono bg-[#1f1f1f] p-3 rounded max-h-32 overflow-auto"
                    >
                        {pix.pix_copia_cola}
                    </div>
                </div>

                <button
                    onClick={copy}
                    data-testid="pix-copy-btn"
                    className="mt-4 w-full py-3 rounded-full bg-[#FFD700] text-black font-bold uppercase tracking-widest text-sm hover:brightness-110 transition-all flex items-center justify-center gap-2"
                >
                    {copied ? <><Check size={16} /> Copiado</> : <><Copy size={16} /> Copiar código</>}
                </button>

                <p className="mt-4 text-xs text-white/40 text-center">
                    Expira em {pix.expires_in_minutes} minutos. O admin confirmará o recebimento.
                </p>
            </div>
            <BottomNav />
        </div>
    );
}
