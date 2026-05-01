"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Define the shape of our User object so TypeScript can auto-complete it
export interface User {
  username: string;
  role: 'STUDENT' | 'SUPERVISOR' | 'ADMINISTRATOR';
}

// Define everything our Context will provide to the rest of the app
interface AuthContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  isLoading: boolean;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// The Provider component that wraps our app
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check localStorage on initial load so users stay logged in after a refresh
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error("Failed to parse stored user data.", error);
      }
    }
    setIsLoading(false);
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    // Set a dummy token so our axiosClient has something to attach to headers
    localStorage.setItem('token', 'dev-jwt-token-12345'); 
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    router.push('/login'); // Kick them back to the login page immediately
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {/* We only render the children once we've checked localStorage to prevent flash of wrong UI */}
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to make importing the context much easier in other files
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};