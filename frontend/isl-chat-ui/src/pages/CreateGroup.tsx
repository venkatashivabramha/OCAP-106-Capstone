import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createGroup, getContacts } from '../services/api';
import { ArrowLeft, Users, Plus, Check } from 'lucide-react';
import '../styles/CreateGroup.css';

interface Contact {
  id: string;
  contact_user_id: string;
  display_name: string;
  phone_number: string;
}

function CreateGroup() {
  const navigate = useNavigate();
  const [groupName, setGroupName] = useState('');
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContacts, setSelectedContacts] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    try {
      const contactsList = await getContacts();
      setContacts(contactsList);
    } catch (error) {
      console.error('Failed to load contacts:', error);
      setError('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const toggleContact = (contactId: string) => {
    setSelectedContacts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(contactId)) {
        newSet.delete(contactId);
      } else {
        newSet.add(contactId);
      }
      return newSet;
    });
  };

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }

    if (selectedContacts.size < 1) {
      setError('Please select at least 1 contact');
      return;
    }

    setCreating(true);
    setError('');

    try {
      const participantIds = Array.from(selectedContacts);
      const group = await createGroup(groupName, participantIds);
      
      console.log('Group created:', group);
      alert(`Group "${groupName}" created successfully!`);
      
      // Navigate back to chat list
      navigate('/chat');
    } catch (error: any) {
      console.error('Failed to create group:', error);
      setError(error.response?.data?.error || 'Failed to create group');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return <div className="create-group loading">Loading contacts...</div>;
  }

  return (
    <div className="create-group">
      {/* Header */}
      <div className="create-group-header">
        <button onClick={() => navigate('/chat')} className="back-button">
          <ArrowLeft size={24} />
        </button>
        <h2>
          <Users size={24} />
          Create Group
        </h2>
      </div>

      <form onSubmit={handleCreateGroup} className="create-group-form">
        {/* Group Name */}
        <div className="group-name-section">
          <div className="group-icon">
            <Users size={48} />
          </div>
          <input
            type="text"
            placeholder="Group Name"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            maxLength={100}
            required
            className="group-name-input"
          />
        </div>

        {/* Selected Count */}
        <div className="selected-count">
          <span>
            {selectedContacts.size} member{selectedContacts.size !== 1 ? 's' : ''} selected
          </span>
        </div>

        {/* Contacts List */}
        <div className="contacts-section">
          <h3>Select Members</h3>
          {contacts.length === 0 ? (
            <div className="no-contacts">
              <p>No contacts available</p>
              <button
                type="button"
                onClick={() => navigate('/chat')}
                className="add-contact-button"
              >
                <Plus size={20} />
                Add Contacts First
              </button>
            </div>
          ) : (
            <div className="contacts-list">
              {contacts.map((contact) => (
                <div
                  key={contact.id}
                  className={`contact-item ${selectedContacts.has(contact.contact_user_id) ? 'selected' : ''}`}
                  onClick={() => toggleContact(contact.contact_user_id)}
                >
                  <div className="contact-avatar">
                    {contact.display_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="contact-info">
                    <div className="contact-name">{contact.display_name}</div>
                    <div className="contact-phone">{contact.phone_number}</div>
                  </div>
                  <div className="contact-checkbox">
                    {selectedContacts.has(contact.contact_user_id) && (
                      <Check size={20} color="#00d856" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && <div className="error-message">{error}</div>}

        {/* Create Button */}
        <button
          type="submit"
          disabled={creating || !groupName.trim() || selectedContacts.size < 1}
          className="create-button"
        >
          {creating ? 'Creating Group...' : 'Create Group'}
        </button>
      </form>
    </div>
  );
}

export default CreateGroup;
