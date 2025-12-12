'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_CONTACTS } from '@/lib/queries';
import { Contact, getContactDisplayName, getInfluencePercentage, getScoreColor } from '@/types';
import { Loader2, Mail, Phone, Building2, MapPin, Users, Target, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ContactDetailPage() {
  const params = useParams();
  const contactId = params.id as string;
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadContact() {
      try {
        setLoading(true);
        // Fetch all contacts and find the one with matching ID
        const data = await fetchQuery<{ contacts: Contact[] }>(GET_CONTACTS, { limit: 10000 });
        const found = data.contacts.find(c => c.id === contactId);
        
        if (!found) {
          setError('Contact not found');
        } else {
          setContact(found);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load contact');
        console.error('Failed to fetch contact:', err);
      } finally {
        setLoading(false);
      }
    }

    loadContact();
  }, [contactId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading contact...</span>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error</h3>
        <p className="text-red-600">{error || 'Contact not found'}</p>
        <Link 
          href="/dashboard/contacts"
          className="inline-flex items-center gap-2 mt-4 text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Contacts
        </Link>
      </div>
    );
  }

  const influencePercentage = getInfluencePercentage(contact.influenceScore);

  return (
    <div>
      {/* Back Button */}
      <Link 
        href="/dashboard/contacts"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Contacts
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {getContactDisplayName(contact)}
            </h1>
            {contact.organization && (
              <div className="flex items-center gap-2 text-gray-600 mb-4">
                <Building2 className="w-5 h-5" />
                <span>{contact.organization}</span>
              </div>
            )}
          </div>

          {/* Influence Score Badge */}
          <div className={`px-4 py-2 rounded-full border-2 ${getScoreColor(contact.influenceScore)}`}>
            <div className="text-sm font-medium text-gray-600">Influence Score</div>
            <div className="text-2xl font-bold">{influencePercentage}%</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Contact Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-3">
              {contact.email && (
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <a href={`mailto:${contact.email}`} className="text-blue-600 hover:text-blue-700">
                    {contact.email}
                  </a>
                </div>
              )}
              {contact.phone && (
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <a href={`tel:${contact.phone}`} className="text-blue-600 hover:text-blue-700">
                    {contact.phone}
                  </a>
                </div>
              )}
              {contact.address && (
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                  <span className="text-gray-700">{contact.address}</span>
                </div>
              )}
            </div>
          </div>

          {/* Network Metrics */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Network Metrics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-gray-200 rounded p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">Connections</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {contact.connectionsCount || 0}
                </div>
              </div>
              
              <div className="border border-gray-200 rounded p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <Target className="w-4 h-4" />
                  <span className="text-sm">Influence Score</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {contact.influenceScore?.toFixed(3) || '0.000'}
                </div>
              </div>
            </div>

            {/* Influence Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Influence Level</span>
                <span>{influencePercentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    influencePercentage >= 70
                      ? 'bg-green-500'
                      : influencePercentage >= 30
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${influencePercentage}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Community */}
          {contact.communityId !== null && contact.communityId !== undefined && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Community</h3>
              <div className="bg-blue-50 border border-blue-200 rounded p-3 text-center">
                <div className="text-sm text-gray-600 mb-1">Member of</div>
                <div className="text-2xl font-bold text-blue-600">
                  Community #{contact.communityId}
                </div>
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Metadata</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-600">ID:</span>
                <div className="font-mono text-xs text-gray-800 break-all mt-1">
                  {contact.id}
                </div>
              </div>
              {contact.createdAt && (
                <div>
                  <span className="text-gray-600">Created:</span>
                  <div className="text-gray-800">
                    {new Date(contact.createdAt).toLocaleDateString()}
                  </div>
                </div>
              )}
              {contact.updatedAt && (
                <div>
                  <span className="text-gray-600">Updated:</span>
                  <div className="text-gray-800">
                    {new Date(contact.updatedAt).toLocaleDateString()}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {contact.email && (
                <a
                  href={`mailto:${contact.email}`}
                  className="block px-4 py-2 bg-white border border-gray-300 rounded text-center hover:bg-gray-50 transition-colors"
                >
                  Send Email
                </a>
              )}
              <Link
                href={`/dashboard/graph?highlight=${contact.id}`}
                className="block px-4 py-2 bg-white border border-gray-300 rounded text-center hover:bg-gray-50 transition-colors"
              >
                View in Network
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
