import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Users, Shield, Check, X, AlertTriangle } from 'lucide-react';

const AdminDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user: currentUser } = useAuth();

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
        fetchUsers();
    }, []);

    const handleRoleChange = async (userId, currentStatus) => {
        if (userId === currentUser.id) {
            alert("You cannot change your own role.");
            return;
        }

        if (!window.confirm(`Are you sure you want to ${currentStatus ? 'demote' : 'promote'} this user?`)) {
            return;
        }

        try {
            await authService.updateUserRole(userId, !currentStatus);
            // Refresh list
            fetchUsers();
        } catch (err) {
            alert("Failed to update role.");
        }
    };

    if (loading) return <div className="p-6">Loading users...</div>;
    if (error) return <div className="p-6 text-red-600">{error}</div>;

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                            <Shield className="mr-2 text-blue-600" />
                            Admin Dashboard
                        </h2>
                        <p className="text-gray-500 mt-1">
                            Manage registered users and their roles.
                        </p>
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
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.full_name}</td>
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
                                        {user.is_superuser ? (
                                            <span className="flex items-center text-purple-600 font-medium">
                                                <Shield size={14} className="mr-1" /> Admin
                                            </span>
                                        ) : (
                                            <span className="text-gray-500">User</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <button
                                            onClick={() => handleRoleChange(user.id, user.is_superuser)}
                                            disabled={user.id === currentUser.id}
                                            className={`text-xs px-3 py-1 rounded border transition-colors ${user.id === currentUser.id
                                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                    : user.is_superuser
                                                        ? 'bg-white border-red-200 text-red-600 hover:bg-red-50'
                                                        : 'bg-white border-blue-200 text-blue-600 hover:bg-blue-50'
                                                }`}
                                        >
                                            {user.is_superuser ? 'Demote to User' : 'Promote to Admin'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
