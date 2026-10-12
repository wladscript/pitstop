import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider, useAuth } from "./lib/auth";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Garage from "./pages/client/Garage";
import NewOrder from "./pages/client/NewOrder";
import OrdersList from "./pages/client/OrdersList";
import OrderDetail from "./pages/client/OrderDetail";
import Pix from "./pages/client/Pix";
import Loyalty from "./pages/client/Loyalty";

import Kanban from "./pages/admin/Kanban";
import OrderDetailAdmin from "./pages/admin/OrderDetailAdmin";
import Units from "./pages/admin/Units";
import Services from "./pages/admin/Services";
import Clients from "./pages/admin/Clients";

function RootRedirect() {
    const { user, checked } = useAuth();
    if (!checked)
        return <div className="min-h-screen flex items-center justify-center text-white/60">Carregando…</div>;
    if (!user) return <Navigate to="/login" replace />;
    return <Navigate to={user.role === "admin" ? "/admin" : "/garagem"} replace />;
}

function App() {
    return (
        <div className="App">
            <AuthProvider>
                <BrowserRouter>
                    <Toaster
                        position="top-center"
                        theme="dark"
                        toastOptions={{
                            style: {
                                background: "#141414",
                                border: "1px solid rgba(255,255,255,0.1)",
                                color: "#fff",
                            },
                        }}
                    />
                    <Routes>
                        <Route path="/" element={<RootRedirect />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/registrar" element={<Register />} />

                        <Route
                            path="/garagem"
                            element={
                                <ProtectedRoute role="cliente">
                                    <Garage />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/novo-pedido"
                            element={
                                <ProtectedRoute role="cliente">
                                    <NewOrder />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/pedidos"
                            element={
                                <ProtectedRoute role="cliente">
                                    <OrdersList />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/pedidos/:id"
                            element={
                                <ProtectedRoute role="cliente">
                                    <OrderDetail />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/pedidos/:id/pix"
                            element={
                                <ProtectedRoute role="cliente">
                                    <Pix />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/fidelidade"
                            element={
                                <ProtectedRoute role="cliente">
                                    <Loyalty />
                                </ProtectedRoute>
                            }
                        />

                        <Route
                            path="/admin"
                            element={
                                <ProtectedRoute role="admin">
                                    <Kanban />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/os/:id"
                            element={
                                <ProtectedRoute role="admin">
                                    <OrderDetailAdmin />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/unidades"
                            element={
                                <ProtectedRoute role="admin">
                                    <Units />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/servicos"
                            element={
                                <ProtectedRoute role="admin">
                                    <Services />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/clientes"
                            element={
                                <ProtectedRoute role="admin">
                                    <Clients />
                                </ProtectedRoute>
                            }
                        />
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </div>
    );
}

export default App;
