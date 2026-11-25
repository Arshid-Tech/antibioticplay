import apiClient from './api';

export default {
  getCategories() {
    return apiClient.get('/flashcards/categories');
  },

  getCards({ category = 'all', mode = 'due', limit = 50 } = {}) {
    return apiClient.get('/flashcards/due', {
      params: { category, mode, limit },
    });
  },

  submitReview(flashcardId, rating) {
    return apiClient.post('/flashcards/review', {
      flashcard_id: flashcardId,
      rating,
    });
  },

  toggleBookmark(flashcardId) {
    return apiClient.post('/flashcards/bookmark', {
      flashcard_id: flashcardId,
    });
  },

  getStats() {
    return apiClient.get('/flashcards/stats');
  },
};
