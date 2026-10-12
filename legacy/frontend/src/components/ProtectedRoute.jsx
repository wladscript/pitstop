import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function ProtectedRoute({ children, role }) {
    const { user, checked } = useAuth();
    if (!checked) {
        return (
            <div className="min-h-screen flex items-center justify-center text-white/60">
                Carregando…
            </div>
        );
    }
    if (!user) return <Navigate to="/login" replace />;
    if (role && user.role !== role) {
        return <Navigate to={user.role === "admin" ? "/admin" : "/garagem"} replace />;
    }
    return children;
}
