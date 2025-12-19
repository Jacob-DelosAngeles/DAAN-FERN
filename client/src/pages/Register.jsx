import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Cpu, Network, Database } from 'lucide-react';
import authBg from '../assets/auth_bg.png';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await register(email, password, fullName);
            navigate('/login');
        } catch (err) {
            setError('Failed to register. Please try again.');
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
                    {/* Dark gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0e4c6b]/90 to-transparent"></div>
                </div>

                <div className="relative z-10">
                    <h1 className="text-6xl font-black text-white tracking-tighter mb-4 drop-shadow-lg">
                        JOIN THE <br />
                        <span className="text-[#6bc1ff]">NETWORK</span>
                    </h1>
                    <p className="text-xl text-blue-100 font-light max-w-md backdrop-blur-sm bg-black/20 p-4 rounded-lg border-l-4 border-[#6bc1ff]">
                        Become part of the next generation of road infrastructure intelligence.
                    </p>
                </div>

                <div className="relative z-10 grid grid-cols-3 gap-6 text-white/80">
                    <div className="flex flex-col items-center gap-2">
                        <Cpu className="w-8 h-8 text-[#6bc1ff]" />
                        <span className="text-xs uppercase tracking-widest">Smart Core</span>
                    </div>
                    <div className="flex flex-col items-center gap-2">
                        <Network className="w-8 h-8 text-[#6bc1ff]" />
                        <span className="text-xs uppercase tracking-widest">Connectivity</span>
                    </div>
                    <div className="flex flex-col items-center gap-2">
                        <Database className="w-8 h-8 text-[#6bc1ff]" />
                        <span className="text-xs uppercase tracking-widest">Big Data</span>
                    </div>
                </div>
            </div>

            {/* Right Side - Register Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#001219] text-white">
                <div className="max-w-md w-full relative z-10">
                    {/* Decorative glow */}
                    <div className="absolute -top-20 -right-20 w-64 h-64 bg-[#6bc1ff]/20 rounded-full blur-[100px] pointer-events-none"></div>
                    <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-[#0e4c6b]/40 rounded-full blur-[100px] pointer-events-none"></div>

                    <div className="mb-8 text-center">
                        <h2 className="text-3xl font-bold mb-2 tracking-tight">Access Grant Protocol</h2>
                        <p className="text-gray-400">Initialize your account credentials</p>
                    </div>

                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl">
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/50 text-red-200 px-4 py-3 rounded mb-6 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div>
                                <label className="block text-gray-300 text-xs font-bold uppercase tracking-wider mb-2" htmlFor="fullName">
                                    Full Name
                                </label>
                                <input
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#6bc1ff] focus:ring-1 focus:ring-[#6bc1ff] transition-all duration-300"
                                    id="fullName"
                                    type="text"
                                    placeholder="John Doe"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    required
                                />
                            </div>

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
                                    placeholder="Create secure password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>

                            <button
                                className="w-full bg-[#6bc1ff] hover:bg-[#5aaee0] text-[#001219] font-bold py-3 px-4 rounded-lg transform hover:-translate-y-0.5 transition-all duration-200 shadow-[0_0_20px_rgba(107,193,255,0.3)] hover:shadow-[0_0_30px_rgba(107,193,255,0.5)] mt-2"
                                type="submit"
                            >
                                ESTABLISH CONNECTION
                            </button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-sm text-gray-400">
                                Already registered?{' '}
                                <Link to="/login" className="text-[#6bc1ff] hover:text-[#9cd6ff] font-semibold transition-colors">
                                    Access Login
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
