import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = authService.getCurrentUser();
        if (token) {
            try {
                const decoded = jwtDecode(token);
                // Check if token is expired
                if (decoded.exp * 1000 < Date.now()) {
                    authService.logout();
                    setUser(null);
                } else {
                    // Decode role from token
                    const role = decoded.role || 'user';
                    setUser({ 
                        email: decoded.sub, 
                        role: role,
                        // Helper properties for easy access
                        is_superuser: role === 'superuser',
                        is_admin: role === 'superuser' || role === 'admin'
                    });
                }
            } catch (error) {
                authService.logout();
                setUser(null);
            }
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            const response = await authService.login(email, password);
            // Decode the new token to get role
            const decoded = jwtDecode(response.access_token);
            const role = decoded.role || 'user';
            setUser({ 
                email, 
                role: role,
                is_superuser: role === 'superuser',
                is_admin: role === 'superuser' || role === 'admin'
            });
            return true;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        }
    };

    const register = async (email, password, fullName) => {
        try {
            await authService.register(email, password, fullName);
            return true;
        } catch (error) {
            console.error("Registration failed", error);
            throw error;
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);

