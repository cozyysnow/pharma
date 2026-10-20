import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Pill, Lock, Mail, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Card, CardContent } from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types/auth';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('admin@pharmastock.local');
  const [password, setPassword] = useState('password123');
  const [selectedRole, setSelectedRole] = useState<UserRole>('ADMIN');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }
    setError(null);
    setIsLoading(true);

    setTimeout(() => {
      login(email, selectedRole);
      setIsLoading(false);
      navigate('/');
    }, 600);
  };

  return (
    <div className="min-h-screen bg-surface-page flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md">
        {/* Brand header */}
        <div className="text-center mb-8">
          <div className="inline-flex w-12 h-12 rounded-xl bg-teal-700 text-white items-center justify-center shadow-lg shadow-teal-900/20 mb-3">
            <Pill className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            PharmaStock IQ
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Pharmacy Stock-Out Prediction & Decision Support System
          </p>
        </div>

        {/* Login Card */}
        <Card className="border-slate-200/90 shadow-xl bg-white">
          <CardContent className="p-6 sm:p-8">
            <div className="mb-6">
              <h2 className="text-base font-semibold text-slate-900">Sign in to your account</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Authorized clinical pharmacy personnel only
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-center gap-2 text-xs text-rose-700">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail className="w-4 h-4" />}
                placeholder="name@pharmastock.local"
                required
              />

              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="w-4 h-4" />}
                placeholder="••••••••"
                required
              />

              <div className="pt-1">
                <label className="text-xs font-medium text-slate-700 block mb-1.5">
                  Demo Sign-In Role
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['ADMIN', 'INVENTORY_MANAGER', 'PHARMACY_STAFF'] as UserRole[]).map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => {
                        setSelectedRole(r);
                        if (r === 'ADMIN') setEmail('admin@pharmastock.local');
                        if (r === 'INVENTORY_MANAGER') setEmail('manager@pharmastock.local');
                        if (r === 'PHARMACY_STAFF') setEmail('staff@pharmastock.local');
                      }}
                      className={`text-[11px] py-1.5 px-2 rounded-lg border font-medium transition-all ${
                        selectedRole === r
                          ? 'border-teal-700 bg-teal-50 text-teal-800 shadow-xs'
                          : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {r === 'ADMIN' ? 'Admin' : r === 'INVENTORY_MANAGER' ? 'Manager' : 'Staff'}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="w-full mt-4"
              >
                Sign In
              </Button>
            </form>

            <div className="mt-6 pt-5 border-t border-slate-100 text-center">
              <div className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                <ShieldCheck className="w-4 h-4 text-teal-600" />
                <span>Role-Based Access Control Enforced</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Persistent notice */}
        <p className="text-[11px] text-slate-400 text-center mt-6">
          Decision support only. All procurement actions require human verification.
        </p>
      </div>
    </div>
  );
};
