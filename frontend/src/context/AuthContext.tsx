import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, UserRole, AuthContextType } from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEFAULT_USERS: Record<UserRole, User> = {
  ADMIN: {
    id: 1,
    name: 'Dr. Sarah Mitchell',
    email: 'admin@pharmastock.local',
    role: 'ADMIN',
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  INVENTORY_MANAGER: {
    id: 2,
    name: 'Rajesh Sharma',
    email: 'manager@pharmastock.local',
    role: 'INVENTORY_MANAGER',
    isActive: true,
    createdAt: '2024-01-15T00:00:00Z',
  },
  PHARMACY_STAFF: {
    id: 3,
    name: 'Ananya Patel',
    email: 'staff@pharmastock.local',
    role: 'PHARMACY_STAFF',
    isActive: true,
    createdAt: '2024-02-01T00:00:00Z',
  },
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRoleState] = useState<UserRole>(() => {
    const saved = localStorage.getItem('pharma_role') as UserRole;
    return saved && DEFAULT_USERS[saved] ? saved : 'ADMIN';
  });

  const [user, setUser] = useState<User | null>(() => DEFAULT_USERS[role]);

  useEffect(() => {
    setUser(DEFAULT_USERS[role]);
    localStorage.setItem('pharma_role', role);
  }, [role]);

  const setRole = (newRole: UserRole) => {
    setRoleState(newRole);
  };

  const login = (_email: string, targetRole: UserRole = 'ADMIN') => {
    setRoleState(targetRole);
    setUser(DEFAULT_USERS[targetRole]);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        login,
        logout,
        setRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
