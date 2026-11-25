import apiClient from './api';

export default {
  getDailyChallenge() {
    return apiClient.get('/challenges/daily');
  },

  submitDailyAnswer(questionId, answer, isLastQuestion) {
    return apiClient.post('/challenges/daily/submit', {
      questionId,
      answer,
      isLastQuestion,
    });
  },

  createDuel(quizId, score) {
    return apiClient.post('/challenges/duel/create', {
      quizId,
      score,
    });
  },

  getDuel(duelId) {
    return apiClient.get(`/challenges/duel/${duelId}`);
  },

  submitDuel(duelId, score) {
    return apiClient.post(`/challenges/duel/${duelId}/submit`, {
      score,
    });
  },
};
