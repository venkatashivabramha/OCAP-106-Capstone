import React, { createContext, useContext, useState, useEffect } from 'react';
import { getProfile, updateProfile as apiUpdate, logout as apiLogout } from '../services/api';

interface User { id: number; username: string; phone_number: string; display_name?: string; bio?: string; avatar_url?: string; }
interface AuthCtx { user: User|null; isAuthenticated: boolean; loading: boolean; login:(u:User)=>void; logout:()=>Promise<void>; updateUserProfile:(name:string,bio?:string)=>Promise<void>; refreshProfile:()=>Promise<void>; }

const AuthContext = createContext<AuthCtx|undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser]       = useState<User|null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const raw   = localStorage.getItem('user');
      const token = localStorage.getItem('access_token');
      if (raw && token) {
        const u = JSON.parse(raw);
        setUser(u);
        try {
          // Validate token by fetching profile
          const p = await getProfile();
          setUser({ ...u, display_name: p.display_name, bio: p.bio, avatar_url: p.avatar_url });
        } catch (err: any) {
          // 401 means stale token — clear and force re-login
          if (err?.response?.status === 401) {
            localStorage.clear();
            setUser(null);
          }
        }
      }
      setLoading(false);
    })();
  }, []);

  const login = (u: User) => { setUser(u); localStorage.setItem('user', JSON.stringify(u)); };

  const logout = async () => {
    try { const rt = localStorage.getItem('refresh_token')||''; await apiLogout(rt); } catch {}
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const updateUserProfile = async (name: string, bio?: string) => {
    const p = await apiUpdate(name, bio);
    const updated = { ...user!, display_name: p.display_name, bio: p.bio, avatar_url: p.avatar_url };
    setUser(updated); localStorage.setItem('user', JSON.stringify(updated));
  };

  const refreshProfile = async () => {
    const p = await getProfile();
    const updated = { ...user!, display_name: p.display_name, bio: p.bio, avatar_url: p.avatar_url };
    setUser(updated); localStorage.setItem('user', JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, logout, updateUserProfile, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
