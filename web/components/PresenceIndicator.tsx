/**
 * PresenceIndicator Component - Phase 7.2
 * 
 * Displays list of users currently online in the workspace.
 * Shows avatars, names, and current activity.
 */

import React from 'react';
import { UserPresence } from '../hooks/useWorkspaceSync';

export interface PresenceIndicatorProps {
  users: UserPresence[];
  currentUserId?: string;
  maxDisplay?: number;
  showActivity?: boolean;
  className?: string;
}

export const PresenceIndicator: React.FC<PresenceIndicatorProps> = ({
  users,
  currentUserId,
  maxDisplay = 5,
  showActivity = true,
  className = '',
}) => {
  const displayUsers = users.slice(0, maxDisplay);
  const hiddenCount = users.length - displayUsers.length;

  const getInitials = (name?: string, email?: string): string => {
    if (name) {
      return name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email[0].toUpperCase();
    }
    return '?';
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'online':
        return 'bg-green-500';
      case 'away':
        return 'bg-yellow-500';
      case 'offline':
        return 'bg-gray-400';
      default:
        return 'bg-gray-400';
    }
  };

  const getActivityText = (user: UserPresence): string | null => {
    if (!showActivity) return null;

    if (user.editing_contact_id && user.editing_field) {
      return `editing ${user.editing_field}`;
    }
    if (user.editing_contact_id) {
      return 'editing contact';
    }
    return null;
  };

  return (
    <div className={`presence-indicator ${className}`}>
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600">
          👥 {users.length} online
        </span>

        <div className="flex -space-x-2">
          {displayUsers.map((user) => {
            const isCurrentUser = user.user_id === currentUserId;
            const activity = getActivityText(user);

            return (
              <div
                key={user.user_id}
                className="relative group"
                title={`${user.name || user.email || user.user_id}${activity ? ` - ${activity}` : ''}`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold border-2 ${
                    isCurrentUser
                      ? 'border-blue-500 bg-blue-600'
                      : 'border-white bg-gray-600'
                  }`}
                >
                  {getInitials(user.name, user.email)}
                </div>

                {/* Status indicator */}
                <div
                  className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white ${getStatusColor(
                    user.status
                  )}`}
                />

                {/* Hover tooltip */}
                <div className="absolute left-0 top-10 hidden group-hover:block z-10">
                  <div className="bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                    <div className="font-semibold">{user.name || 'Anonymous'}</div>
                    {user.email && (
                      <div className="text-gray-400">{user.email}</div>
                    )}
                    {activity && (
                      <div className="text-blue-400 italic">{activity}</div>
                    )}
                    {isCurrentUser && (
                      <div className="text-blue-400">(You)</div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Show +N if more users */}
          {hiddenCount > 0 && (
            <div
              className="w-8 h-8 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center text-xs font-semibold text-gray-700"
              title={`${hiddenCount} more users online`}
            >
              +{hiddenCount}
            </div>
          )}
        </div>
      </div>

      {/* Connection status */}
      <div className="flex items-center space-x-1 text-xs text-gray-500">
        <div className={`w-2 h-2 rounded-full ${users.length > 0 ? 'bg-green-500' : 'bg-gray-400'} animate-pulse`} />
        <span>{users.length > 0 ? 'Connected' : 'Disconnected'}</span>
      </div>
    </div>
  );
};

export default PresenceIndicator;
