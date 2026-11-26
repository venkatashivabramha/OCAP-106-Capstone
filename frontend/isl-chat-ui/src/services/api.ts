import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication APIs - Updated for Firebase backend
export const sendOTP = async (phoneNumber: string) => {
  const response = await api.post('/auth/send-otp/', { phone_number: phoneNumber });
  return response.data;
};

export const verifyOTP = async (phoneNumber: string, otp: string) => {
  const response = await api.post('/auth/verify-otp/', {
    phone_number: phoneNumber,
    otp: otp,
  });
  return response.data;
};

export const getProfile = async () => {
  const response = await api.get('/auth/profile/');
  return response.data;
};

export const updateProfile = async (displayName: string, bio?: string) => {
  const response = await api.put('/auth/profile/', {
    display_name: displayName,
    bio: bio || '',
  });
  return response.data;
};

export const logout = async (refreshToken: string) => {
  const response = await api.post('/auth/logout/', {
    refresh_token: refreshToken,
  });
  return response.data;
};

// Contacts APIs
export const getContacts = async () => {
  const response = await api.get('/contacts/');
  return response.data;
};

export const addContact = async (contactPhoneNumber: string, displayName: string) => {
  const response = await api.post('/contacts/', {
    contact_phone_number: contactPhoneNumber,
    display_name: displayName,
  });
  return response.data;
};

// Conversations APIs
export const getConversations = async () => {
  const response = await api.get('/conversations/');
  return response.data;
};

export const createConversation = async (participantPhoneNumbers: string[], isGroup: boolean = false) => {
  const response = await api.post('/conversations/', {
    participant_phone_numbers: participantPhoneNumbers,
    is_group: isGroup,
  });
  return response.data;
};

// Messages APIs
export const getMessages = async (conversationId: string) => {
  const response = await api.get('/messages/', {
    params: { conversation_id: conversationId },
  });
  return response.data;
};

export const sendMessage = async (
  conversationId: string,
  messageType: 'text' | 'sign' | 'audio',
  textContent?: string,
  signLabel?: string,
  confidenceScore?: number,
  mediaUrl?: string
) => {
  const response = await api.post('/messages/', {
    conversation_id: conversationId,
    message_type: messageType,
    text_content: textContent || '',
    sign_label: signLabel,
    confidence_score: confidenceScore,
    media_url: mediaUrl,
  });
  return response.data;
};

export const markMessagesAsRead = async (messageIds: string[]) => {
  const response = await api.patch('/messages/status/', {
    message_ids: messageIds,
    status: 'read',
  });
  return response.data;
};

// Sign Recognition API
export const recognizeSign = async (frameBase64: string) => {
  const response = await api.post('/recognition/recognize/', {
    frame: frameBase64,
  });
  return response.data;
};

// Typing Indicators
export const setTypingIndicator = async (conversationId: string, isTyping: boolean) => {
  const response = await api.post('/typing/set/', {
    conversation_id: conversationId,
    is_typing: isTyping,
  });
  return response.data;
};

export default api;

// Group Chat APIs
export const createGroup = async (groupName: string, participantIds: string[]) => {
  const response = await api.post('/conversations/create-group/', {
    group_name: groupName,
    participant_ids: participantIds,
  });
  return response.data;
};

export const addGroupMember = async (conversationId: string, userId: string) => {
  const response = await api.post(`/conversations/${conversationId}/add-member/`, {
    user_id: userId,
  });
  return response.data;
};

// ===== Phase 2: ISL Chat LLM =====
export const islChat = async (text: string, signs?: string[]) => {
  const response = await api.post('/llm/isl-chat/', { text, signs: signs || [] });
  return response.data;
};

export const addSignToSequence = async (signLabel: string, confidence: number) => {
  const response = await api.post('/recognition/sequence/', { sign_label: signLabel, confidence });
  return response.data;
};

export const flushSignSequence = async () => {
  const response = await api.post('/recognition/flush/', {});
  return response.data;
};
