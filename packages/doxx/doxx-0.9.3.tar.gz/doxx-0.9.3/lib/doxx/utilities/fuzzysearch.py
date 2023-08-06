#!/usr/bin/env python
# encoding: utf-8

import difflib


class FuzzySearcher(object):
    def __init__(self, needle):
        self.needle = needle
        self.needle_normalized = needle.lower().strip()
        self.needle_alpha = self._get_alphabetical_string(self.needle_normalized)
        self.needle_word_count = len(needle.split(" "))
        self.needle_length = len(self.needle_normalized)
    
    # Search Types
    
    # test match to the entire haystack string
    def full_string_ratio(self, haystack):
        normalized_haystack = haystack.lower().strip()
        return difflib.SequenceMatcher(None, self.needle_normalized, normalized_haystack).ratio()
    
    # partial match ratio for first index item after split on '-' character
    def partial_firstindexitem_dashsplit_ratio(self, haystack):
        normalized_haystack = haystack.lower().strip()
        haystack_tokens = normalized_haystack.split('-')
        first_haystack_token = haystack_tokens[0]
        return difflib.SequenceMatcher(None, self.needle_normalized, first_haystack_token).ratio()
    
    # partial match ratio for needle length slice from the haystack
    def partial_startslice_ratio(self, haystack):
        normalized_haystack = haystack.lower().strip()
        needle_length = len(self.needle_normalized)
        if len(normalized_haystack) > needle_length:
            sliced_haystack = normalized_haystack[0:needle_length]
            return difflib.SequenceMatcher(None, self.needle_normalized, sliced_haystack).ratio()
            
        else:
            return difflib.SequenceMatcher(None, self.needle_normalized, normalized_haystack).ratio()
        
    # split haystack into tokens on '-' character delimiters, return best ratio from tokens (use for needle word length = 1)
    def partial_dashsplit_tokens_ratio(self, haystack):
        normalized_haystack = haystack.lower().strip()
        haystack_tokens = normalized_haystack.split("-")
        best_ratio = 0
        for token in haystack_tokens:
            the_ratio = difflib.SequenceMatcher(None, self.needle_normalized, token).ratio()
            if the_ratio > best_ratio:
                best_ratio = the_ratio
        return best_ratio
    
    # attempt match over same number of word tokens as are present in the needle, sorted in alpha order (for multi-word searches)
    def partial_nword_ratio(self, haystack):
        normalized_haystack = haystack.lower().strip()
        haystack_token_list = normalized_haystack.split('-')
        haystack_word_count = len(haystack_token_list)
        if haystack_word_count >= self.needle_word_count:
            first = 0
            last = self.needle_word_count
            best_ratio = 0
            for x in range(haystack_word_count - (self.needle_word_count - 1)):
                if last <= haystack_word_count:
                    sub_haystack_list = haystack_token_list[first:last]
                    sorted_sub_haystack_list = sorted(sub_haystack_list)
                    sorted_sub_haystack_string = " ".join(sorted_sub_haystack_list)
                    token_match_ratio = difflib.SequenceMatcher(None, self.needle_alpha, sorted_sub_haystack_string).ratio()
                    if token_match_ratio > best_ratio:
                        best_ratio = token_match_ratio
                    
                    first += 1  # iterate the positions of the test string slice
                    last += 1
            return best_ratio
        else:
            return difflib.SequenceMatcher(None, self.needle_normalized, normalized_haystack).ratio()
        
    # set intersection between needle and haystack tokens with addition of remaining parts of strings (use > 0.7 as threshold)
    def partial_set_ratio(self, haystack):
        normalized_haystack = haystack.lower().strip()
        haystack_alpha = sorted(normalized_haystack.split('-'))
        haystack_set = set(haystack_alpha)
        needle_set = set(self.needle_alpha.split(" "))
        
        intersection_set = sorted(needle_set.intersection(haystack_set))
        needle_difference = sorted(needle_set.difference(haystack_set))
        haystack_difference = sorted(haystack_set.difference(needle_set))
        
        if len(intersection_set) > 0:
            string_one = " ".join(intersection_set)
            
            if len(needle_difference) > 0:
                string_two = string_one + " " + " ".join(needle_difference)
            else:
                string_two = string_one  # if there were no tokens in difference, it is just the intersection
            
            if len(haystack_difference) > 0:
                string_three = string_one + " " + " ".join(haystack_difference)
            else:
                string_three = string_one  # if there were no tokens in the difference, it is just the intersection
            
            token_match_ratio_one = difflib.SequenceMatcher(None, string_one, string_two).ratio()
            token_match_ratio_two = difflib.SequenceMatcher(None, string_one, string_three).ratio()
            token_match_ratio_three = difflib.SequenceMatcher(None, string_two, string_three).ratio()
            
            # return an evenly weighted average of the match ratios
            weighted_average_ratio = (0.333 * token_match_ratio_one) + (0.333 * token_match_ratio_two) + (0.333 * token_match_ratio_three)
            return weighted_average_ratio
        else:
            return 0  # if there is no intersection tokens between the needle and haystack tokens, return 0
    
    # Utilities
    
    def _get_alphabetical_string(self, pre_string):
        if " " in pre_string:
            alpha_list = sorted(pre_string.split(" "))
            alpha_string = " ".join(alpha_list)
            return alpha_string
        else:
            return pre_string
        
    
    