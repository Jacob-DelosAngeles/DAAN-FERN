import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { LogIn, Activity, Map, ShieldCheck } from 'lucide-react';
import authBg from '../assets/auth_bg.png';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Failed to login. Please check your credentials.');
        }
    };

    return (
        <div className="min-h-screen flex w-full">
            {/* Left Side - Visuals (Hidden on mobile) */}
            <div className="hidden lg:flex w-1/2 relative flex-col justify-between p-12 overflow-hidden">
                <div
                    className="absolute inset-0 z-0"
                    style={{
                        backgroundImage: `url(${authBg})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                    }}
                >
                    {/* Dark overlay to ensure text readability if needed */}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0e4c6b]/90 to-transparent"></div>
                </div>

                <div className="relative z-10">
                    <h1 className="text-6xl font-black text-white tracking-tighter mb-4 drop-shadow-lg">
                        PROJECT <br />
                        <span className="text-[#6bc1ff]">DAAN</span>
                    </h1>
                    <p className="text-xl text-blue-100 font-light max-w-md backdrop-blur-sm bg-black/20 p-4 rounded-lg border-l-4 border-[#6bc1ff]">
                        Digital Analytics and Asset-Based Inspection of Road Networks
                    </p>
                </div>

                <div className="relative z-10 grid grid-cols-3 gap-6 text-white/80">
                    <div className="flex flex-col items-center gap-2">
                        <Activity className="w-8 h-8 text-[#6bc1ff]" />
                        <span className="text-xs uppercase tracking-widest">AI Detection</span>
                    </div>
                    <div className="flex flex-col items-center gap-2">
                        <Map className="w-8 h-8 text-[#6bc1ff]" />
                        <span className="text-xs uppercase tracking-widest">Geotagging</span>
                    </div>
                    <div className="flex flex-col items-center gap-2">
                        <ShieldCheck className="w-8 h-8 text-[#6bc1ff]" />
                        <span className="text-xs uppercase tracking-widest">Asset Mgmt</span>
                    </div>
                </div>
            </div>

            {/* Right Side - Login Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#001219] text-white">
                <div className="max-w-md w-full relative z-10">
                    {/* Decorative glow behind form */}
                    <div className="absolute -top-20 -left-20 w-64 h-64 bg-[#6bc1ff]/20 rounded-full blur-[100px] pointer-events-none"></div>
                    <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-[#0e4c6b]/40 rounded-full blur-[100px] pointer-events-none"></div>

                    <div className="mb-8 text-center">
                        <h2 className="text-4xl font-bold mb-2 tracking-tight">Welcome Back</h2>
                        <p className="text-gray-400">Enter your credentials to access the command center</p>
                    </div>

                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl">
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/50 text-red-200 px-4 py-3 rounded mb-6 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-gray-300 text-xs font-bold uppercase tracking-wider mb-2" htmlFor="email">
                                    Email Address
                                </label>
                                <input
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#6bc1ff] focus:ring-1 focus:ring-[#6bc1ff] transition-all duration-300"
                                    id="email"
                                    type="email"
                                    placeholder="name@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-gray-300 text-xs font-bold uppercase tracking-wider mb-2" htmlFor="password">
                                    Password
                                </label>
                                <input
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#6bc1ff] focus:ring-1 focus:ring-[#6bc1ff] transition-all duration-300"
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>

                            <button
                                className="w-full bg-[#6bc1ff] hover:bg-[#5aaee0] text-[#001219] font-bold py-3 px-4 rounded-lg transform hover:-translate-y-0.5 transition-all duration-200 shadow-[0_0_20px_rgba(107,193,255,0.3)] hover:shadow-[0_0_30px_rgba(107,193,255,0.5)]"
                                type="submit"
                            >
                                INITIATE SESSION
                            </button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-sm text-gray-400">
                                New to the platform?{' '}
                                <Link to="/register" className="text-[#6bc1ff] hover:text-[#9cd6ff] font-semibold transition-colors">
                                    Request Access
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
