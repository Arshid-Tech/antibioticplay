import apiClient from './api';

export default {
  getAnalytics() {
    return apiClient.get('/admin/analytics');
  },

  downloadExport(type) {
    return apiClient.get(`/admin/export/${type}`, { responseType: 'blob' });
  },

  getQuizzes() {
    return apiClient.get('/admin/quizzes');
  },

  createQuiz(data) {
    return apiClient.post('/admin/quizzes', data);
  },

  updateQuiz(quizId, data) {
    return apiClient.put(`/admin/quizzes/${quizId}`, data);
  },

  deleteQuiz(quizId) {
    return apiClient.delete(`/admin/quizzes/${quizId}`);
  },

  createQuestion(data) {
    return apiClient.post('/admin/questions', data);
  },

  updateQuestion(questionId, data) {
    return apiClient.put(`/admin/questions/${questionId}`, data);
  },

  deleteQuestion(questionId) {
    return apiClient.delete(`/admin/questions/${questionId}`);
  },

  getFlashcards() {
    return apiClient.get('/admin/flashcards');
  },

  createFlashcard(data) {
    return apiClient.post('/admin/flashcards', data);
  },

  updateFlashcard(id, data) {
    return apiClient.put(`/admin/flashcards/${id}`, data);
  },

  deleteFlashcard(id) {
    return apiClient.delete(`/admin/flashcards/${id}`);
  },

  getUsers() {
    return apiClient.get('/admin/users');
  },

  updateUserRole(userId, role) {
    return apiClient.put(`/admin/users/${userId}/role`, { role });
  },
};
