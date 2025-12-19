import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Users, Shield, ArrowLeft, Crown, UserCheck, User as UserIcon } from 'lucide-react';

const AdminDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user: currentUser } = useAuth();
    const navigate = useNavigate();

    // Redirect non-superusers
    useEffect(() => {
        if (currentUser && !currentUser.is_superuser) {
            navigate('/dashboard');
        }
    }, [currentUser, navigate]);

    const fetchUsers = async () => {
        try {
            const data = await authService.getUsers();
            setUsers(data);
        } catch (err) {
            setError('Failed to fetch users. You might not have permission.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (currentUser?.is_superuser) {
            fetchUsers();
        }
    }, [currentUser]);

    const handleRoleChange = async (userId, currentRole) => {
        // Can't modify superusers
        if (currentRole === 'superuser') {
            alert("Cannot modify superuser accounts.");
            return;
        }

        const newRole = currentRole === 'admin' ? 'user' : 'admin';
        const action = newRole === 'admin' ? 'promote to Admin' : 'demote to User';

        if (!window.confirm(`Are you sure you want to ${action} this user?`)) {
            return;
        }

        try {
            await authService.updateUserRole(userId, newRole);
            fetchUsers();
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to update role.");
        }
    };

    const getRoleBadge = (role) => {
        switch (role) {
            case 'superuser':
                return (
                    <span className="flex items-center text-purple-600 font-medium">
                        <Crown size={14} className="mr-1" /> Superuser
                    </span>
                );
            case 'admin':
                return (
                    <span className="flex items-center text-blue-600 font-medium">
                        <Shield size={14} className="mr-1" /> Admin
                    </span>
                );
            default:
                return (
                    <span className="flex items-center text-gray-500">
                        <UserIcon size={14} className="mr-1" /> User
                    </span>
                );
        }
    };

    if (!currentUser?.is_superuser) {
        return <div className="p-6 text-red-600">Access denied. Superuser only.</div>;
    }

    if (loading) return <div className="p-6">Loading users...</div>;
    if (error) return <div className="p-6 text-red-600">{error}</div>;

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="mr-4 p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                            title="Back to Dashboard"
                        >
                            <ArrowLeft size={20} />
                        </button>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                                <Shield className="mr-2 text-blue-600" />
                                User Management
                            </h2>
                            <p className="text-gray-500 mt-1">
                                Manage user roles. Admins can upload files. Users have read-only access.
                            </p>
                        </div>
                    </div>
                    <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-md text-sm font-medium">
                        Total Users: {users.length}
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Full Name</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{user.id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.full_name || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        {user.is_active ? (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                Active
                                            </span>
                                        ) : (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                                Inactive
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        {getRoleBadge(user.role)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {user.role === 'superuser' ? (
                                            <span className="text-xs text-gray-400 italic">Protected</span>
                                        ) : (
                                            <button
                                                onClick={() => handleRoleChange(user.id, user.role)}
                                                className={`text-xs px-3 py-1 rounded border transition-colors ${user.role === 'admin'
                                                        ? 'bg-white border-orange-200 text-orange-600 hover:bg-orange-50'
                                                        : 'bg-white border-blue-200 text-blue-600 hover:bg-blue-50'
                                                    }`}
                                            >
                                                {user.role === 'admin' ? 'Demote to User' : 'Promote to Admin'}
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Role Legend */}
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Role Permissions:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="flex items-start">
                            <Crown size={16} className="mr-2 text-purple-600 mt-0.5" />
                            <div>
                                <span className="font-medium text-purple-600">Superuser:</span>
                                <span className="text-gray-600 ml-1">Full access, manage roles</span>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <Shield size={16} className="mr-2 text-blue-600 mt-0.5" />
                            <div>
                                <span className="font-medium text-blue-600">Admin:</span>
                                <span className="text-gray-600 ml-1">Upload/delete files, view data</span>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <UserIcon size={16} className="mr-2 text-gray-500 mt-0.5" />
                            <div>
                                <span className="font-medium text-gray-600">User:</span>
                                <span className="text-gray-600 ml-1">View data only (read-only)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;

