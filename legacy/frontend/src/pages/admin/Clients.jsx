import React, { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { api } from "../../lib/api";
import Sidebar from "../../components/admin/Sidebar";

export default function Clients() {
    const [clientes, setClientes] = useState([]);

    useEffect(() => {
        api.get("/admin/clientes").then((r) => setClientes(r.data));
    }, []);

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-8">
                <h1 className="font-display text-2xl uppercase tracking-tight">Clientes</h1>
                <p className="text-sm text-white/50 mt-1">
                    Base de clientes e pontuação de fidelidade.
                </p>

                <div className="mt-6 rounded-lg bg-[#141414] border border-white/10 overflow-hidden">
                    <table className="w-full text-sm">
                        <thead className="bg-[#1a1a1a] text-white/60 text-xs uppercase tracking-widest">
                            <tr>
                                <th className="text-left px-4 py-3">Nome</th>
                                <th className="text-left px-4 py-3">Telefone</th>
                                <th className="text-right px-4 py-3">Pontos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {clientes.map((c) => (
                                <tr
                                    key={c.id}
                                    data-testid={`client-row-${c.id}`}
                                    className="border-t border-white/5 hover:bg-white/[0.02]"
                                >
                                    <td className="px-4 py-3">{c.nome}</td>
                                    <td className="px-4 py-3 text-white/60">{c.telefone}</td>
                                    <td className="px-4 py-3 text-right">
                                        <span className="inline-flex items-center gap-1 text-[#FFD700]">
                                            <Star size={12} />
                                            {c.pontos_fidelidade}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    );
}
