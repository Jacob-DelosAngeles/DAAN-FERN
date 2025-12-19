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
                    // We need to fetch the full user details to get is_superuser, or include it in the token.
                    // For now, let's fetch the user details from the backend if possible, or assume the token has it if we update the backend.
                    // Actually, the token payload currently only has 'sub' (email). 
                    // Let's update the backend to include 'is_superuser' in the token OR fetch user details here.
                    // Fetching user details is safer.
                    // But wait, we don't have a "get me" endpoint.
                    // Let's assume the login response returns the user object which has it.
                    // But on refresh, we only have the token.
                    // Let's decode the token and if we update the backend to include permissions, that's best.
                    // For now, let's try to fetch the user list and find ourselves (inefficient but works for now) OR add a /me endpoint.
                    // Adding a /me endpoint is best practice.
                    // But to save time/complexity, I'll update the backend to include `is_superuser` in the JWT.
                    setUser({ email: decoded.sub, is_superuser: decoded.is_superuser });
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
            // Decode the new token to get updated permissions
            const decoded = jwtDecode(response.access_token);
            setUser({ email, is_superuser: decoded.is_superuser });
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
