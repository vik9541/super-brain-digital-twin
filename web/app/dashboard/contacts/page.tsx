'use client';

import { useEffect, useState } from 'react';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_CONTACTS } from '@/lib/queries';
import { Contact } from '@/types';
import ContactTable from '@/components/ContactTable';
import { Loader2, Users } from 'lucide-react';

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadContacts() {
      try {
        setLoading(true);
        const data = await fetchQuery<{ contacts: Contact[] }>(
          GET_CONTACTS,
          { limit: 1000 } // Load more contacts for better search experience
        );
        setContacts(data.contacts);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load contacts');
        console.error('Failed to fetch contacts:', err);
      } finally {
        setLoading(false);
      }
    }

    loadContacts();
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Contacts</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <Users className="w-8 h-8 text-blue-600" />
            Contacts
          </h1>
          <p className="text-gray-600">
            {loading ? 'Loading...' : `${contacts.length.toLocaleString()} total contacts in database`}
          </p>
        </div>
      </div>

      {/* Contacts Table */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[400px] bg-white rounded-lg shadow-md">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading contacts...</span>
        </div>
      ) : (
        <ContactTable contacts={contacts} />
      )}
    </div>
  );
}
