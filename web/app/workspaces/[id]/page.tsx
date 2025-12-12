'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import {
    GET_WORKSPACE,
    INVITE_MEMBER,
    REMOVE_MEMBER,
    GET_WORKSPACE_ACTIVITY
} from '@/lib/graphql/queries';

export default function WorkspaceDetailPage() {
    const params = useParams();
    const workspaceId = params.id as string;

    const [showInviteForm, setShowInviteForm] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteRole, setInviteRole] = useState('MEMBER');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Queries
    const { data: workspaceData, loading, refetch } = useQuery(GET_WORKSPACE, {
        variables: { id: workspaceId }
    });

    const { data: activityData } = useQuery(GET_WORKSPACE_ACTIVITY, {
        variables: { workspaceId, page: 1, perPage: 20 }
    });

    // Mutations
    const [inviteMember, { loading: inviting }] = useMutation(INVITE_MEMBER, {
        onCompleted: (data) => {
            setSuccess(data.inviteMember.message);
            setInviteEmail('');
            setInviteRole('MEMBER');
            setShowInviteForm(false);
            refetch();
            setTimeout(() => setSuccess(''), 3000);
        },
        onError: (err) => {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    });

    const [removeMember] = useMutation(REMOVE_MEMBER, {
        onCompleted: () => {
            setSuccess('Member removed');
            refetch();
            setTimeout(() => setSuccess(''), 3000);
        },
        onError: (err) => {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    });

    const handleInviteMember = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!inviteEmail.trim()) {
            setError('Email is required');
            return;
        }

        await inviteMember({
            variables: {
                workspaceId,
                email: inviteEmail,
                role: inviteRole
            }
        });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-gray-600">Loading workspace...</div>
            </div>
        );
    }

    const workspace = workspaceData?.workspace;
    const activity = activityData?.workspaceActivity?.entries || [];

    if (!workspace) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-gray-600">Workspace not found</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">{workspace.name}</h1>
                            <p className="text-gray-600 mt-1">
                                Plan: <span className="font-semibold">{workspace.plan}</span>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Messages */}
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

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column - Members */}
                    <div className="lg:col-span-2">
                        {/* Members Section */}
                        <Card className="p-6 mb-8">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-xl font-bold">Team Members ({workspace.memberCount})</h2>
                                <Button
                                    onClick={() => setShowInviteForm(!showInviteForm)}
                                    className="btn btn-primary"
                                >
                                    + Invite Member
                                </Button>
                            </div>

                            {/* Invite Form */}
                            {showInviteForm && (
                                <form onSubmit={handleInviteMember} className="mb-6 p-4 bg-gray-50 rounded-lg border">
                                    <div className="grid grid-cols-3 gap-4 mb-4">
                                        <Input
                                            type="email"
                                            value={inviteEmail}
                                            onChange={(e) => setInviteEmail(e.target.value)}
                                            placeholder="email@example.com"
                                            className="col-span-2"
                                        />
                                        <Select
                                            value={inviteRole}
                                            onChange={(e) => setInviteRole(e.target.value)}
                                        >
                                            <option value="MEMBER">Member</option>
                                            <option value="ADMIN">Admin</option>
                                            <option value="VIEWER">Viewer</option>
                                        </Select>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button
                                            type="submit"
                                            disabled={inviting}
                                            className="btn btn-primary"
                                        >
                                            {inviting ? 'Inviting...' : 'Send Invite'}
                                        </Button>
                                        <Button
                                            type="button"
                                            onClick={() => setShowInviteForm(false)}
                                            className="btn btn-secondary"
                                        >
                                            Cancel
                                        </Button>
                                    </div>
                                </form>
                            )}

                            {/* Members List */}
                            <div className="space-y-3">
                                {workspace.members.map((member: any) => (
                                    <div
                                        key={member.userId}
                                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                                    >
                                        <div className="flex-1">
                                            <p className="font-medium text-gray-900">{member.email}</p>
                                            <p className="text-sm text-gray-600">
                                                {member.name} • {member.role}
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="inline-block px-2 py-1 text-xs font-semibold text-blue-700 bg-blue-100 rounded">
                                                {member.role}
                                            </span>
                                            {member.role !== 'OWNER' && (
                                                <Button
                                                    onClick={() =>
                                                        removeMember({
                                                            variables: {
                                                                workspaceId,
                                                                memberId: member.userId
                                                            }
                                                        })
                                                    }
                                                    className="text-red-600 hover:text-red-800"
                                                >
                                                    Remove
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Card>

                        {/* Activity Log */}
                        <Card className="p-6">
                            <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
                            <div className="space-y-3">
                                {activity.length === 0 ? (
                                    <p className="text-gray-600">No activity yet</p>
                                ) : (
                                    activity.slice(0, 10).map((entry: any) => (
                                        <div key={entry.id} className="flex items-start gap-3 pb-3 border-b last:border-b-0">
                                            <div className="flex-1">
                                                <p className="text-sm font-medium text-gray-900">
                                                    {entry.action}
                                                </p>
                                                <p className="text-sm text-gray-600">
                                                    {entry.description}
                                                </p>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    {new Date(entry.createdAt).toLocaleString()}
                                                </p>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </Card>
                    </div>

                    {/* Right Column - Stats */}
                    <div>
                        <Card className="p-6">
                            <h3 className="text-lg font-bold mb-4">Workspace Stats</h3>
                            <div className="space-y-4">
                                <div>
                                    <p className="text-sm text-gray-600">Members</p>
                                    <p className="text-3xl font-bold text-blue-600">{workspace.memberCount}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">Plan</p>
                                    <p className="text-2xl font-bold">{workspace.plan}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">Created</p>
                                    <p className="text-sm font-medium">
                                        {new Date(workspace.createdAt).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
