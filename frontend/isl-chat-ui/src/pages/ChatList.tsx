import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getConversations, createConversation, getProfile, logout } from '../services/api';
import { MessageCircle, Plus, LogOut, User, Users, Search } from 'lucide-react';
import '../styles/ChatList.css';

interface ChatListProps {
  onLogout: () => void;
}

interface Conversation {
  id: string;
  conversation_type: string;
  group_name?: string;
  last_message_at?: string;
  last_message?: string;
  participants: any[];
}

function ChatList({ onLogout }: ChatListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [filtered, setFiltered]           = useState<Conversation[]>([]);
  const [loading, setLoading]             = useState(true);
  const [showNewChat, setShowNewChat]     = useState(false);
  const [newChatPhone, setNewChatPhone]   = useState('');
  const [search, setSearch]              = useState('');
  const [user, setUser]                  = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => { loadData(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(q ? conversations.filter(c => getConversationName(c).toLowerCase().includes(q)) : conversations);
  }, [search, conversations]);

  const loadData = async () => {
    try {
      const [convs, profile] = await Promise.all([getConversations(), getProfile()]);
      setConversations(convs);
      setFiltered(convs);
      setUser(profile);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartNewChat = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let phone = newChatPhone.trim();
      if (!phone.startsWith('+')) phone = '+91' + phone;
      const conv = await createConversation([phone], false);
      navigate(`/chat/${conv.id}`);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to create conversation');
    }
  };

  const handleLogout = async () => {
    try {
      const rt = localStorage.getItem('refresh_token') || '';
      await logout(rt);
    } catch {}
    localStorage.clear();
    onLogout();
  };

  const formatTime = (ts?: string) => {
    if (!ts) return '';
    const d = new Date(ts);
    const diff = Date.now() - d.getTime();
    if (diff < 86_400_000) return d.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
    return d.toLocaleDateString([], { month:'short', day:'numeric' });
  };

  const getConversationName = (conv: Conversation) => {
    if (conv.conversation_type === 'group') return conv.group_name || 'Group Chat';
    const other = conv.participants?.find((p: any) => p.user_id !== user?.id);
    return other?.user?.full_name || other?.user?.phone_number || 'Chat';
  };

  const getAvatar = (name: string) => name.charAt(0).toUpperCase();

  if (loading) return <div className="cl-loading"><div className="spinner" /><p>Loading chats...</p></div>;

  return (
    <div className="cl-container">
      {/* ── Header ── */}
      <div className="cl-header">
        <h1>🤟 ISL Chat</h1>
        <div className="cl-header-actions">
          <button className="cl-icon-btn" onClick={() => navigate('/create-group')} title="New Group">
            <Users size={22} />
          </button>
          <button className="cl-icon-btn" title="Profile">
            <User size={22} />
          </button>
          <button className="cl-icon-btn cl-logout" onClick={handleLogout} title="Logout">
            <LogOut size={22} />
          </button>
        </div>
      </div>

      {/* ── Search ── */}
      <div className="cl-search">
        <Search size={16} className="cl-search-icon" />
        <input
          placeholder="Search chats..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* ── New Chat ── */}
      <div className="cl-new-chat">
        <button className="cl-new-btn" onClick={() => setShowNewChat(!showNewChat)}>
          <Plus size={18} /> New Chat
        </button>
      </div>

      {showNewChat && (
        <form className="cl-new-form" onSubmit={handleStartNewChat}>
          <input
            type="tel"
            placeholder="+919876543210"
            value={newChatPhone}
            onChange={e => setNewChatPhone(e.target.value)}
            required
            autoFocus
          />
          <button type="submit" className="cl-btn-primary">Start</button>
          <button type="button" className="cl-btn-secondary" onClick={() => setShowNewChat(false)}>Cancel</button>
        </form>
      )}

      {/* ── Conversation List ── */}
      <div className="cl-list">
        {filtered.length === 0 ? (
          <div className="cl-empty">
            <MessageCircle size={56} />
            <h3>No Conversations</h3>
            <p>{search ? 'No results found' : 'Start a new chat!'}</p>
          </div>
        ) : (
          filtered.map(conv => (
            <div key={conv.id} className="cl-item" onClick={() => navigate(`/chat/${conv.id}`)}>
              <div className="cl-avatar">{getAvatar(getConversationName(conv))}</div>
              <div className="cl-info">
                <div className="cl-row">
                  <span className="cl-name">{getConversationName(conv)}</span>
                  <span className="cl-time">{formatTime(conv.last_message_at)}</span>
                </div>
                <p className="cl-preview">{conv.last_message || '🤟 Tap to start signing...'}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ChatList;
