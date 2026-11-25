import apiClient from './api';

export default {
  getStatus() {
    return apiClient.get('/survey/status');
  },

  submitSurvey(payload) {
    return apiClient.post('/survey/submit', payload);
  },
};
