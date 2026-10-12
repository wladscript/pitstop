import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { formatApiError } from "../lib/api";
import { Zap } from "lucide-react";

export default function Login() {
    const { login } = useAuth();
    const nav = useNavigate();
    const [telefone, setTelefone] = useState("");
    const [senha, setSenha] = useState("");
    const [err, setErr] = useState("");
    const [loading, setLoading] = useState(false);

    const submit = async (e) => {
        e.preventDefault();
        setErr("");
        setLoading(true);
        try {
            const u = await login(telefone, senha);
            nav(u.role === "admin" ? "/admin" : "/garagem");
        } catch (e) {
            setErr(formatApiError(e.response?.data?.detail) || e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-stretch">
            <div
                className="hidden md:block flex-1 bg-cover bg-center relative"
                style={{
                    backgroundImage:
                        "url(https://images.unsplash.com/photo-1607860108855-64acf2078ed9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzN8MHwxfHNlYXJjaHw0fHxjYXIlMjB3YXNoJTIwZGV0YWlsaW5nJTIwbHV4dXJ5fGVufDB8fHx8MTc5MTgxODE4N3ww&ixlib=rb-4.1.0&q=85)",
                }}
            >
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-black/20" />
                <div className="absolute bottom-12 left-12 right-12">
                    <h2 className="font-display text-5xl uppercase tracking-tighter text-white leading-none">
                        O brilho<br />não espera.
                    </h2>
                    <p className="text-white/60 mt-4 max-w-md">
                        Agende, acompanhe e pague a lavagem do seu carro em segundos.
                    </p>
                </div>
            </div>

            <div className="flex-1 flex items-center justify-center px-6 py-10 bg-[#0a0a0a]">
                <div className="w-full max-w-sm">
                    <div className="flex items-center gap-2 mb-10">
                        <div className="w-9 h-9 rounded-md bg-[#0066FF] flex items-center justify-center">
                            <Zap size={20} />
                        </div>
                        <div className="font-display text-2xl uppercase tracking-tight">
                            Pit Stop
                        </div>
                    </div>
                    <h1 className="font-display text-4xl uppercase tracking-tighter">
                        Entrar
                    </h1>
                    <p className="text-white/50 mt-2 text-sm">
                        Use seu telefone e senha para acessar.
                    </p>

                    <form onSubmit={submit} className="mt-8 space-y-4">
                        <div>
                            <label className="text-xs uppercase tracking-widest text-white/50">
                                Telefone
                            </label>
                            <input
                                data-testid="login-phone-input"
                                value={telefone}
                                onChange={(e) => setTelefone(e.target.value)}
                                placeholder="11999999999"
                                className="mt-1 w-full bg-[#141414] border border-white/10 rounded-md px-4 py-3 text-white placeholder:text-white/30 focus:border-[#0066FF] focus:ring-1 focus:ring-[#0066FF] outline-none transition-colors"
                                required
                            />
                        </div>
                        <div>
                            <label className="text-xs uppercase tracking-widest text-white/50">
                                Senha
                            </label>
                            <input
                                data-testid="login-password-input"
                                type="password"
                                value={senha}
                                onChange={(e) => setSenha(e.target.value)}
                                className="mt-1 w-full bg-[#141414] border border-white/10 rounded-md px-4 py-3 text-white focus:border-[#0066FF] focus:ring-1 focus:ring-[#0066FF] outline-none transition-colors"
                                required
                            />
                        </div>

                        {err && (
                            <div
                                data-testid="login-error"
                                className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-2 rounded"
                            >
                                {err}
                            </div>
                        )}

                        <button
                            data-testid="login-submit-btn"
                            disabled={loading}
                            className="w-full py-3 rounded-full bg-[#0066FF] hover:bg-[#3385FF] text-white font-semibold uppercase tracking-widest text-sm transition-colors disabled:opacity-50"
                        >
                            {loading ? "Entrando…" : "Entrar"}
                        </button>
                    </form>

                    <div className="mt-6 text-sm text-white/50">
                        Novo por aqui?{" "}
                        <Link
                            to="/registrar"
                            data-testid="go-to-register-link"
                            className="text-[#3385FF] hover:underline"
                        >
                            Criar conta
                        </Link>
                    </div>

                    <div className="mt-10 text-xs text-white/30 border-t border-white/10 pt-4">
                        <div>Demo admin: 11999999999 / admin123</div>
                        <div>Demo cliente: 11988887777 / demo123</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
