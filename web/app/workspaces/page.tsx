'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import {
    GET_MY_WORKSPACES,
    CREATE_WORKSPACE,
    DELETE_WORKSPACE
} from '@/lib/graphql/queries';

export default function WorkspacesPage() {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspacePlan, setNewWorkspacePlan] = useState('PRO');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Query workspaces
    const { data, loading, refetch } = useQuery(GET_MY_WORKSPACES, {
        variables: { page: 1, perPage: 10 }
    });

    // Create workspace mutation
    const [createWorkspace, { loading: creating }] = useMutation(CREATE_WORKSPACE, {
        onCompleted: (data) => {
            setSuccess('Workspace created successfully!');
            setNewWorkspaceName('');
            setShowCreateForm(false);
            refetch();
            setTimeout(() => setSuccess(''), 3000);
        },
        onError: (err) => {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    });

    // Delete workspace mutation
    const [deleteWorkspace] = useMutation(DELETE_WORKSPACE, {
        onCompleted: () => {
            setSuccess('Workspace deleted');
            refetch();
            setTimeout(() => setSuccess(''), 3000);
        },
        onError: (err) => {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    });

    const handleCreateWorkspace = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!newWorkspaceName.trim()) {
            setError('Workspace name is required');
            return;
        }

        await createWorkspace({
            variables: {
                name: newWorkspaceName,
                plan: newWorkspacePlan
            }
        });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-gray-600">Loading workspaces...</div>
            </div>
        );
    }

    const workspaces = data?.myWorkspaces?.workspaces || [];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex justify-between items-center">
                        <h1 className="text-3xl font-bold text-gray-900">Workspaces</h1>
                        <Button
                            onClick={() => setShowCreateForm(!showCreateForm)}
                            className="btn btn-primary"
                        >
                            + New Workspace
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Error/Success Messages */}
                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                        {error}
                    </div>
                )}
                {success && (
                    <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
                        {success}
                    </div>
                )}

                {/* Create Workspace Form */}
                {showCreateForm && (
                    <Card className="mb-8 p-6">
                        <h2 className="text-xl font-bold mb-4">Create New Workspace</h2>
                        <form onSubmit={handleCreateWorkspace} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Workspace Name
                                </label>
                                <Input
                                    type="text"
                                    value={newWorkspaceName}
                                    onChange={(e) => setNewWorkspaceName(e.target.value)}
                                    placeholder="Enter workspace name"
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Plan
                                </label>
                                <Select
                                    value={newWorkspacePlan}
                                    onChange={(e) => setNewWorkspacePlan(e.target.value)}
                                >
                                    <option value="FREE">Free</option>
                                    <option value="PRO">Pro</option>
                                    <option value="ENTERPRISE">Enterprise</option>
                                </Select>
                            </div>

                            <div className="flex gap-2">
                                <Button
                                    type="submit"
                                    disabled={creating}
                                    className="btn btn-primary"
                                >
                                    {creating ? 'Creating...' : 'Create Workspace'}
                                </Button>
                                <Button
                                    type="button"
                                    onClick={() => setShowCreateForm(false)}
                                    className="btn btn-secondary"
                                >
                                    Cancel
                                </Button>
                            </div>
                        </form>
                    </Card>
                )}

                {/* Workspaces Grid */}
                {workspaces.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-600 mb-4">No workspaces yet</p>
                        <Button
                            onClick={() => setShowCreateForm(true)}
                            className="btn btn-primary"
                        >
                            Create your first workspace
                        </Button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {workspaces.map((ws: any) => (
                            <Link key={ws.id} href={`/workspaces/${ws.id}`}>
                                <a className="block">
                                    <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="text-lg font-bold text-gray-900">{ws.name}</h3>
                                            <span className="inline-block px-2 py-1 text-xs font-semibold text-white bg-blue-600 rounded">
                                                {ws.plan}
                                            </span>
                                        </div>

                                        <p className="text-gray-600 text-sm mb-4">
                                            {ws.memberCount} member{ws.memberCount !== 1 ? 's' : ''}
                                        </p>

                                        <div className="mb-4">
                                            <h4 className="text-xs font-semibold text-gray-700 uppercase mb-2">Members</h4>
                                            <div className="flex flex-wrap gap-1">
                                                {ws.members.slice(0, 3).map((member: any) => (
                                                    <div
                                                        key={member.userId}
                                                        className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                                                    >
                                                        {member.email}
                                                    </div>
                                                ))}
                                                {ws.memberCount > 3 && (
                                                    <div className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                                        +{ws.memberCount - 3} more
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex justify-between items-center text-xs text-gray-500">
                                            <span>
                                                Created {new Date(ws.createdAt).toLocaleDateString()}
                                            </span>
                                            <Button
                                                type="button"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    deleteWorkspace({ variables: { id: ws.id } });
                                                }}
                                                className="text-red-600 hover:text-red-800"
                                            >
                                                Delete
                                            </Button>
                                        </div>
                                    </Card>
                                </a>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
