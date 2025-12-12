/**
 * TypingIndicator Component - Phase 7.2
 * 
 * Shows when other users are typing in a field.
 * Displays "User is typing..." with animated dots.
 */

import React, { useState, useEffect } from 'react';

export interface TypingUser {
  user_id: string;
  user_name?: string;
  user_email?: string;
  contact_id?: string;
  field?: string;
  is_typing: boolean;
}

export interface TypingIndicatorProps {
  contactId?: string;
  field?: string;
  className?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  contactId,
  field,
  className = '',
}) => {
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);

  useEffect(() => {
    const handleTyping = (event: CustomEvent<TypingUser>) => {
      const { contact_id, field: typingField, user_id, user_name, is_typing } = event.detail;

      // Filter by contactId and field if provided
      if (contactId && contact_id !== contactId) return;
      if (field && typingField !== field) return;

      setTypingUsers((prev) => {
        // Remove user if stopped typing
        if (!is_typing) {
          return prev.filter((u) => u.user_id !== user_id);
        }

        // Add or update user
        const existing = prev.find((u) => u.user_id === user_id);
        if (existing) {
          return prev.map((u) =>
            u.user_id === user_id
              ? { ...u, user_name, field: typingField, contact_id }
              : u
          );
        }

        return [
          ...prev,
          {
            user_id,
            user_name,
            contact_id,
            field: typingField,
            is_typing: true,
          },
        ];
      });

      // Auto-remove after 3 seconds of inactivity
      setTimeout(() => {
        setTypingUsers((prev) =>
          prev.filter((u) => u.user_id !== user_id || !u.is_typing)
        );
      }, 3000);
    };

    window.addEventListener('workspace:typing', handleTyping as EventListener);

    return () => {
      window.removeEventListener('workspace:typing', handleTyping as EventListener);
    };
  }, [contactId, field]);

  if (typingUsers.length === 0) {
    return null;
  }

  const getUserNames = (): string => {
    if (typingUsers.length === 1) {
      return typingUsers[0].user_name || 'Someone';
    }
    if (typingUsers.length === 2) {
      return `${typingUsers[0].user_name || 'Someone'} and ${typingUsers[1].user_name || 'someone else'}`;
    }
    return `${typingUsers.length} people`;
  };

  return (
    <div className={`typing-indicator flex items-center space-x-2 text-sm text-gray-600 ${className}`}>
      <span>{getUserNames()} {typingUsers.length === 1 ? 'is' : 'are'} typing</span>
      
      {/* Animated dots */}
      <div className="flex space-x-1">
        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
};

export default TypingIndicator;
