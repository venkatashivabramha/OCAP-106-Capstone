// LLM Service - AI-powered features using Ollama
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/llm';

const llmApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token
llmApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Check LLM service status
export const checkLLMStatus = async () => {
  try {
    const response = await llmApi.get('/status/');
    return response.data;
  } catch (error) {
    console.error('LLM status check failed:', error);
    return { available: false };
  }
};

// Translate sign sequence to English
export const translateSigns = async (signs: string[]) => {
  try {
    const response = await llmApi.post('/translate-signs/', { signs });
    return response.data;
  } catch (error) {
    console.error('Sign translation failed:', error);
    return { translation: signs.join(' '), source: 'fallback' };
  }
};

// Convert English to ISL grammar
export const convertToISL = async (text: string) => {
  try {
    const response = await llmApi.post('/convert-to-isl/', { text });
    return response.data;
  } catch (error) {
    console.error('ISL conversion failed:', error);
    return { isl_format: text.toUpperCase(), source: 'fallback' };
  }
};

// Get AI response suggestions
export const getSuggestions = async (context: any[], numSuggestions = 3) => {
  try {
    const response = await llmApi.post('/suggest-responses/', {
      context,
      num_suggestions: numSuggestions,
    });
    return response.data;
  } catch (error) {
    console.error('Suggestions failed:', error);
    return { suggestions: ['Thank you!', 'I understand', 'Tell me more'], source: 'fallback' };
  }
};

// Get sign explanation
export const explainSign = async (signName: string) => {
  try {
    const response = await llmApi.post('/explain-sign/', { sign: signName });
    return response.data;
  } catch (error) {
    console.error('Sign explanation failed:', error);
    return { 
      explanation: `Please refer to ISL dictionary for '${signName}'`,
      source: 'fallback' 
    };
  }
};

// Summarize conversation
export const summarizeConversation = async (messages: any[]) => {
  try {
    const response = await llmApi.post('/summarize/', { messages });
    return response.data;
  } catch (error) {
    console.error('Summarization failed:', error);
    return { summary: `Conversation with ${messages.length} messages`, source: 'fallback' };
  }
};
