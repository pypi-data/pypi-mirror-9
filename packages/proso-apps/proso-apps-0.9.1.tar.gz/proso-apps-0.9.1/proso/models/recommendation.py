import abc
import random
import math
import logging
import proso.django.log
from collections import defaultdict


LOGGER = logging.getLogger('django.request')


class Recommendation:

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def recommend(self, environment, user, items, time, n, **kwargs):
        pass


class RandomRecommendation(Recommendation):

    def __init__(self, predictive_model):
        self._predictive_model = predictive_model

    def recommend(self, environment, user, items, time, n, **kwargs):
        candidates = random.sample(items, n)
        if kwargs.get('options'):
            return candidates, map(lambda item: self._options(item, items), candidates)
        else:
            return candidates

    def _options(self, item, items):
        items = list(items)
        items.remove(item)
        return random.sample(items, random.randint(1, 5))

    def __str__(self):
        return 'RANDOM RECOMMENDATION'


class ScoreRecommendation(Recommendation):

    def __init__(
            self, predictive_model, weight_probability=10.0, weight_number_of_answers=5.0,
            weight_time_ago=120, weight_parent_time_ago=120, weight_parent_number_of_answers=2.5,
            target_probability=0.8, recompute_parent_score=True):
        self._predictive_model = predictive_model
        self._weight_probability = weight_probability
        self._weight_number_of_answers = weight_number_of_answers
        self._weight_time_ago = weight_time_ago
        self._target_probability = target_probability
        self._weight_parent_time_ago = weight_parent_time_ago
        self._weight_parent_number_of_answers = weight_parent_number_of_answers
        self._recompute_parent_score = recompute_parent_score

    def recommend(self, environment, user, items, time, n, **kwargs):
        answers_num = dict(zip(items, environment.number_of_answers_more_items(user=user, items=items)))
        last_answer_time = dict(zip(items, environment.last_answer_time_more_items(user=user, items=items)))
        probability = dict(zip(items, self._predictive_model.predict_more_items(environment, user, items, time)))
        parents = dict(zip(items, environment.get_items_with_values_more_items('parent', items=items)))
        # The current implementation of retrieving features for the parent
        # items provides only an under-approximation of the real state.
        last_answer_time_parents = self._last_answer_time_for_parents(environment, parents, last_answer_time)
        answers_num_parents = self._answers_num_for_parents(environment, parents, answers_num)
        rolling_success = environment.rolling_success(user=user)
        prob_target = self._adjust_target_probability(rolling_success)

        if proso.django.log.is_active():
            for item in items:
                if len(parents.get(item, [])) == 0:
                    LOGGER.warn("The item %s has no parent" % item)

        def _score(item):
            return (
                self._weight_probability * self._score_probability(prob_target, probability[item]) +
                self._weight_time_ago * self._score_last_answer_time(last_answer_time[item], time) +
                self._weight_number_of_answers * self._score_answers_num(answers_num[item]),
                random.random()
            )

        def _finish_score(((score, r), i)):
            total = 0.0
            parent_time_score = 0.0
            parent_answers_num_score = 0.0
            for p, v in parents[i]:
                parent_time_score += v * self._score_last_answer_time(last_answer_time_parents[p], time)
                parent_answers_num_score += v * self._score_answers_num(answers_num_parents[p])
                total += 1
            if total > 0:
                parent_time_score = parent_time_score / total
                parent_answers_num_score = parent_answers_num_score / total
            score += self._weight_parent_time_ago * parent_time_score
            score += self._weight_parent_number_of_answers * parent_answers_num_score
            return (score, r), i

        scored = zip(map(_score, items), items)
        if self._recompute_parent_score:
            candidates = []
            while len(candidates) < n and len(scored) > 0:
                finished = map(_finish_score, scored)
                score, chosen = max(finished)
                if proso.django.log:
                    LOGGER.debug(
                        'recommending %s (total_score %.2f, prob score %.2f, time_score %.2f, answers score %.2f, parents %s)' %
                        (
                            chosen, score[0],
                            self._weight_probability * self._score_probability(prob_target, probability[chosen]),
                            self._weight_time_ago * self._score_last_answer_time(last_answer_time[chosen], time),
                            self._weight_number_of_answers * self._score_answers_num(answers_num[chosen]),
                            map(lambda x: x[0], parents[chosen]))
                        )
                candidates.append(chosen)
                for p, v in parents[chosen]:
                    last_answer_time_parents[p] = time
                scored = filter(lambda (score, i): i != chosen, scored)
        else:
            candidates = map(lambda ((score, r), i): i, sorted(scored, reverse=True)[:min(len(scored), n)])

        if kwargs.get('options', False):
            return candidates, map(
                lambda item: self._options(environment, item, probability, rolling_success), candidates)
        else:
            return candidates

    def _score_answers_num(self, answers_num):
        return 1.0 / max(math.sqrt(answers_num), 0.001)

    def _score_probability(self, target_probability, probability):
        diff = target_probability - probability
        sign = 1 if diff > 0 else -1
        normed_diff = abs(diff) / max(0.001, abs(target_probability - 0.5 + sign * 0.5))
        return 1 - normed_diff

    def _score_last_answer_time(self, last_answer_time, time):
        if last_answer_time is None:
            seconds_ago = 315360000
        else:
            seconds_ago = (time - last_answer_time).total_seconds()
        return - 1.0 / max(seconds_ago, 0.001)

    def _adjust_target_probability(self, rolling_success):
        norm = 1 - self._target_probability if rolling_success > self._target_probability else self._target_probability
        correction = ((self._target_probability - rolling_success) / max(0.001, norm)) * (1 - norm)
        return self._target_probability + correction

    def _answers_num_for_parents(self, environment, parents, answers_num):
        children = defaultdict(list)
        for i, ps in parents.iteritems():
            for p, v in ps:
                children[p].append(i)

        return dict(map(
            lambda (p, chs): (p, sum(map(lambda ch: answers_num[ch], chs))),
            children.items()))

    def _last_answer_time_for_parents(self, environment, parents, last_answer_time):
        children = defaultdict(list)
        for i, ps in parents.iteritems():
            for p, v in ps:
                children[p].append(i)

        def _max_time_from_items(xs):
            times = filter(lambda x: x is not None, map(lambda x: last_answer_time[x], xs))
            if len(times) > 0:
                return max(times)
            else:
                return None
        return dict(map(lambda (p, chs): (p, _max_time_from_items(chs)), children.items()))

    def _options(self, environment, item, items_with_prediction, rolling_success):
        # number of options
        round_fun = round
        prob_real = items_with_prediction[item]
        prob_target = self._adjust_target_probability(rolling_success)
        g = min(0.5, max(0, prob_target - prob_real) / max(0.001, 1 - prob_real))
        k = round_fun(1.0 / g) if g != 0 else 1
        number_of_options = int(0 if (k > 6 or k == 0) else (k - 1))
        if number_of_options == 0:
            return []
        # confusing places
        confusing_factor = environment.confusing_factor_more_items(item, items_with_prediction.keys())
        confusing_factor_total = float(sum(confusing_factor))
        confusing_places = map(lambda (a, b): (b, a), sorted(zip(confusing_factor, items_with_prediction.keys()), reverse=True))
        # options
        result_options = []
        for i in range(number_of_options):
            prob_sum = 0
            random_dice = random.uniform(0, confusing_factor_total)
            for i, conf_factor in confusing_places:
                if i in result_options or i == item:
                    continue
                prob_sum += conf_factor
                if random_dice > prob_sum:
                    result_options.append(i)
                    confusing_factor_total -= conf_factor
                    break
        return result_options + [item]

    def __str__(self):
        return 'SCORE RECOMMENDATION: target probability {0:.2f}, weight probability {1:.2f}, weight time {2:.2f}, weight answers {3:.2f}'.format(
            self._target_probability, self._weight_probability, self._weight_time_ago, self._weight_number_of_answers)
