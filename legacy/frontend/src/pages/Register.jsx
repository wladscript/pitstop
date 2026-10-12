import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { formatApiError } from "../lib/api";
import { Zap } from "lucide-react";

export default function Register() {
    const { register } = useAuth();
    const nav = useNavigate();
    const [nome, setNome] = useState("");
    const [telefone, setTelefone] = useState("");
    const [senha, setSenha] = useState("");
    const [err, setErr] = useState("");
    const [loading, setLoading] = useState(false);

    const submit = async (e) => {
        e.preventDefault();
        setErr("");
        setLoading(true);
        try {
            await register(nome, telefone, senha);
            nav("/garagem");
        } catch (e) {
            setErr(formatApiError(e.response?.data?.detail) || e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-6 py-10">
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
                    Criar conta
                </h1>
                <p className="text-white/50 mt-2 text-sm">
                    Comece a cuidar do seu carro agora.
                </p>

                <form onSubmit={submit} className="mt-8 space-y-4">
                    <div>
                        <label className="text-xs uppercase tracking-widest text-white/50">
                            Nome
                        </label>
                        <input
                            data-testid="register-name-input"
                            value={nome}
                            onChange={(e) => setNome(e.target.value)}
                            className="mt-1 w-full bg-[#141414] border border-white/10 rounded-md px-4 py-3 focus:border-[#0066FF] focus:ring-1 focus:ring-[#0066FF] outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="text-xs uppercase tracking-widest text-white/50">
                            Telefone
                        </label>
                        <input
                            data-testid="register-phone-input"
                            value={telefone}
                            onChange={(e) => setTelefone(e.target.value)}
                            placeholder="11988887777"
                            className="mt-1 w-full bg-[#141414] border border-white/10 rounded-md px-4 py-3 focus:border-[#0066FF] focus:ring-1 focus:ring-[#0066FF] outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="text-xs uppercase tracking-widest text-white/50">
                            Senha
                        </label>
                        <input
                            data-testid="register-password-input"
                            type="password"
                            value={senha}
                            onChange={(e) => setSenha(e.target.value)}
                            className="mt-1 w-full bg-[#141414] border border-white/10 rounded-md px-4 py-3 focus:border-[#0066FF] focus:ring-1 focus:ring-[#0066FF] outline-none"
                            required
                            minLength={4}
                        />
                    </div>

                    {err && (
                        <div
                            data-testid="register-error"
                            className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-2 rounded"
                        >
                            {err}
                        </div>
                    )}

                    <button
                        data-testid="register-submit-btn"
                        disabled={loading}
                        className="w-full py-3 rounded-full bg-[#0066FF] hover:bg-[#3385FF] font-semibold uppercase tracking-widest text-sm transition-colors disabled:opacity-50"
                    >
                        {loading ? "Criando…" : "Criar conta"}
                    </button>
                </form>

                <div className="mt-6 text-sm text-white/50">
                    Já tem conta?{" "}
                    <Link
                        to="/login"
                        data-testid="go-to-login-link"
                        className="text-[#3385FF] hover:underline"
                    >
                        Entrar
                    </Link>
                </div>
            </div>
        </div>
    );
}
