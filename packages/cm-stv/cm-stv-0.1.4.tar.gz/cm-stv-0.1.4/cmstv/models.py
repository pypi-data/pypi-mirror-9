import math

def almostEqual(v1, v2, diff=0.0001):
    return abs(v1-v2) < diff

def assertAlmostEqual(v1, v2, diff=0.0001):
    assert almostEqual(v1, v2, diff), '%f and %f were more than %f apart' % (v1, v2, diff)

class Candidate(object):
    
    def __init__(self, name, slate=None):
        self.name = name
        self.slate = slate
    
    def __str__(self):
        if self.slate:
            return '{} ({})'.format(self.name, self.slate)
        else:
            return self.name
    
    def __repr__(self):
        return '{}({}, {})'.format(self.__class__, self.name, self.slate)
    
class Ballot(object):
    
    def __init__(self, candidates=[], weight=1.0, original_candidates=None):
        assert weight >= 0
        self.candidates = list(candidates)
        self.original_candidates = list(original_candidates if original_candidates else candidates)
        self.weight = weight
    
    def reset_weight(self):
        self.weight = 1.0
    
    def reset_candidates(self):
        self.candidates = list(self.original_candidates)
    
    def pop_next(self):
        try:
            return self.candidates.pop(0)
        except IndexError:
            return None
    
    def __add__(self, other):
        return self.weight+other
    
    def __radd__(self, other):
        return self.__add__(other)
        
    def __repr__(self):
        return '{}({} with {})'.format(self.__class__, self.weight, self.original_candidates)
        
class DroopQuota(object):
    
    def calculate(self, ballots, num_seats):
        assert num_seats > 0
        return math.floor((len(ballots)/(num_seats+1.0))+1.0)
        
class GregorySurplus(object):
    
    def __init__(self, sum_ballots, quota):
        '''Initializes the Gregory Surplus Allocation method with two 
        factors, surplus_multiplier and elected_multipler such that:
        
        |<------------------->|<-------->|
        0      ^            quota   ^   sum_ballots
          sum_ballots          sum_ballots
               x                    x
        elected_multiplier   surplus_multiplier
        
        '''
        assert sum_ballots >= quota and sum_ballots > 0
        self.surplus_multiplier = (sum_ballots-quota)/float(sum_ballots)
        self.elected_multiplier = 1 - self.surplus_multiplier
    
    def adjust_to_surplus_weight(self, ballot):
        ballot.weight = ballot.weight * self.surplus_multiplier
    
    def adjust_to_elected_weight(self, ballot):
        ballot.weight = ballot.weight * self.elected_multiplier
    
class Race(object):
    
    def __init__(self, candidates, num_seats=1, ballots=set(), quota=None, minimum=0, tie_breakers=None):
        '''Create a race with a list of candidates, num_seats to elect, and a list of ballots, and Droop Quota by default
        '''
        assert num_seats > 0
        
        if not quota:
            quota = DroopQuota().calculate(ballots, num_seats)
            
        self.ballots = set(ballots)
        self.num_seats = num_seats
        self.quota = quota
        self.minimum = minimum
        if not tie_breakers:
            self.candidate_tie_breakers = list(candidates)
        else:
            self.candidate_tie_breakers = list(tie_breakers)
        
        # Generate a dict of sets for each candidate to keep track of ballots voting for each candidate: {candidate: set(), ...}
        self.hopefuls = dict((candidate, set()) for candidate in candidates)
        
        # Initialize
        self.elected = []
        self.excluded = []
        self.rejected = []
        self.exhausted_ballots = set()
        self.rounds = []
    
    def init_ballots(self):
        '''Moves each ballot to the set of the first choice candidate
        self.hopefuls = {candidate: {ballot, ...}, ...}
        '''
        for ballot in self.ballots:
            ballot.reset_candidates()
            self.transfer_to_next_candidate(ballot)
    
    def transfer_to_next_candidate(self, ballot):
        '''Add a ballot to the set of the next hopeful candidate on it.
        If there is no next candidate, adds the ballot to the exhausted set.
        Returns the candidate transferred to or None
        '''
        candidate = ballot.pop_next()
        hopefuls = self.hopefuls.keys()
        # Find next candidate that has not been excluded or elected.
        while candidate and candidate not in hopefuls:
            candidate = ballot.pop_next()
        if candidate:
            self.hopefuls[candidate].add(ballot)
            return candidate
        else:
            self.exhausted_ballots.add(ballot)
            return None
    
    def transfer(self, ballots):
        '''Transfers the ballots to the next available candidate or the exhausted set
        and records totals, returning them in the format:
        {'candidates': {candidate: tally}, 'exhausted': tally}
        '''
        transfers = {'candidates': {}, 'exhausted': 0}
        for ballot in ballots:
            to_candidate = self.transfer_to_next_candidate(ballot)
            if to_candidate:
                transfers['candidates'][to_candidate] = transfers['candidates'].get(to_candidate, 0)+ballot.weight
            else:
                transfers['exhausted']+=ballot.weight
        return transfers
    
    def elect(self, candidate, ballots, transfer_surplus=True):
        '''Elects a candidate, reweighting the ballots given via the Gregory Method
        and transferring them to the next candidate if needed. The elected candidate 
        and the ballots used to elect them are added to the elected list.
        Returns the tranfers made if any.
        '''
        sum_ballots = sum(ballots)
        assert sum_ballots >= 0
        if transfer_surplus and sum_ballots >= self.quota:
            assert len(ballots) > 0
            # Initialize Gregory Allocation
            gregory = GregorySurplus(sum_ballots, self.quota)
            
            # Add candidate to elected with a copy of the ballots used to elect them at adjusted weights
            # Copy ballots
            ballots_used = set(Ballot(candidates=list(b.candidates), original_candidates=list(b.original_candidates), weight=b.weight) for b in ballots)
            # Adjust ballot weights
            for ballot in ballots_used:
                gregory.adjust_to_elected_weight(ballot)
            # Check the ballot weights
            assertAlmostEqual(sum(ballots_used), self.quota)
            
            # Record election
            self.elected.append({'candidate': candidate, 'ballots_used': ballots_used})
            
            # Transfer surplus ballots at new weight
            # Adjust weights
            for ballot in ballots:
                gregory.adjust_to_surplus_weight(ballot)
            # Check weights
            assertAlmostEqual(sum(ballots), sum_ballots-self.quota)
            transfers = self.transfer(ballots)
            
            # Check that the sum of weights used to elect and the sum of weights 
            # transferred equals the sum of original weights
            assertAlmostEqual(sum(ballots)+sum(ballots_used), sum_ballots)
        else:
            # Candidate is being elected without meeting quota so
            # simply elect them with ballots at current weight
            self.elected.append({'candidate': candidate, 'ballots_used': ballots})
            transfers = None
        return transfers
    
    def exclude(self, candidate, ballots):
        '''Excludes a candidate, transferring their ballots to the next candidate.
        The excluded candidate is added to the excluded list.
        Returns the transfers made.
        '''
        transfers = self.transfer(ballots)
        self.excluded.append(candidate)
        
        return transfers

    def reject(self, candidate, ballots):
        '''Rejects a candidate, adding the candidate and ballots to the rejected list'''
        self.rejected.append({'candidate': candidate, 'ballots': ballots})
        return None
        
    def get_sorted_hopefuls(self):
        '''Sorts the candidates based on their tallies in descending order
        Maps:
        hopefuls.iteritems() = [(candidate, ballots), ...]
        to:
        sorted_hopefuls = [(tally, candidate, ballots) from highest tally to lowest]
        '''
        sorted_hopefuls = map(lambda x: (sum(x[1]), x[0], x[1]), self.hopefuls.iteritems())
        sorted_hopefuls.sort(reverse=True)
        return sorted_hopefuls
    
    def get_top_candidates(self, sorted_hopefuls):
        sorted_hopefuls = list(sorted_hopefuls)
        
        for i in range(len(sorted_hopefuls)):
            # Get top sum
            top_sum = sorted_hopefuls[0][0]
            # Get candidates that match the top sum
            top_candidates = dict((candidate, (sum_ballots, candidate, ballots)) for (sum_ballots, candidate, ballots) in sorted_hopefuls if almostEqual(sum_ballots, top_sum))
            # Make sure all candidates are accounted for in tie breakers
            assert all(c in self.candidate_tie_breakers for c in top_candidates), 'All candidates must be in tie breaking list'
            # Sort the candidates based on the order in the tie breakers
            orig_len = len(sorted_hopefuls)
            candidate = next(c for c in self.candidate_tie_breakers if c in top_candidates)
            sorted_hopefuls.remove(top_candidates[candidate])
            assert len(sorted_hopefuls) == orig_len - 1
            yield top_candidates[candidate] + ({'break_tie': set(top_candidates.keys())} if len(top_candidates) > 1 else None,)
    
    def next_candidate_to_exclude(self, sorted_hopefuls):
        '''Returns the next candidate to be excluded with their ballots, breaking any ties for last, in the following format
        (
            [(candidate, ballots), ...],
            {
                'break_tie': {candidate, ...}
            }
            or
            None
        )
        '''
        # Get the lowest sum
        lowest_sum = sorted_hopefuls[-1][0]
        # Get candidates that match the lowest sum
        lowest_candidates = dict((candidate, (sum_ballots, candidate, ballots)) for (sum_ballots, candidate, ballots) in sorted_hopefuls if almostEqual(sum_ballots, lowest_sum))
        # Make sure all candidates are accounted for in tie breakers
        assert all(c in self.candidate_tie_breakers for c in lowest_candidates), 'All candidates must be in tie breaking list'        
        # Find the first candidate in the tie breakers with the sum
        candidate = next(c for c in self.candidate_tie_breakers if c in lowest_candidates)
        return lowest_candidates[candidate] + ({'break_tie': set(lowest_candidates.keys())} if len(lowest_candidates) > 1 else None,)
    
    def get_status(self):
        '''Gets the status of the race in the format
        {
            'elected': [candidate, ...],
            'excluded': [candidate, ...],
            'hopefuls': [(candidate, tally) from high tally to lowest], 
            'num_seats': num_seats,
            'quota': quota, 
            'minimum': minimum,
            'exhausted': num_exhausted
        }
        '''
        return {'quota': self.quota, 
                'elected': list(self.elected), # Clone current elected
                'excluded': list(self.excluded),  # Clone current excluded
                'hopefuls': [(candidate, ballot_sum) for (ballot_sum, candidate, ballots) in self.get_sorted_hopefuls()],
                'num_seats': self.num_seats,
                'quota': self.quota,
                'minimum': self.minimum,
                'exhausted': sum(self.exhausted_ballots)}
    
    def get_candidate_count(self):
        '''Returns the total number of candidates in the race'''
        return len(self.hopefuls)+len(self.elected)+len(self.excluded)+len(self.rejected)
    
    def get_total_ballot_tally(self):
        '''Returns the total tally of all the ballots being used in the race'''
        return (sum(sum(ballots) for ballots in self.hopefuls.values()) # Ballots belonging to hopefuls
                + sum(sum(e['ballots_used']) for e in self.elected) # Ballots used to elect
                + sum(sum(r['ballots']) for r in self.rejected) # Ballots belonging to rejected
                + sum(self.exhausted_ballots)) # Ballots that have been exhausted
    
    def run_round(self):
        '''Runs a round of the election. Either elects all hopefuls that 
        have met the quota or excludes the lowest candidate. Preference is 
        given to electing over excluding. Checks for any ties.
        Returns a list of actions taken in the following format
        [
            {'break_tie': {candidate, ...}},
            or
            {'elect': candidate, 'transfer': transfers},
            or
            {'exclude': candidate, 'transfer': transfers},
            ...
        ]
        '''
        old_candidate_count = self.get_candidate_count()
        old_ballot_tally = self.get_total_ballot_tally()
        
        sorted_hopefuls = self.get_sorted_hopefuls()
        actions = []
        
        # Determines which candidates have met the quota.
        # Removes them from hopefuls immediately to prevent
        # surplus ballots from transferring to them when 
        # others are elected while there is still room. 
        # This behavior should be reviewed for correctness.
        candidates_to_be_elected = []
        for (sum_ballots, candidate, ballots, break_tie) in self.get_top_candidates(sorted_hopefuls):
            if sum_ballots >= self.quota and self.still_have_open_seats(candidates_to_be_elected):
                self.hopefuls.pop(candidate)
                if break_tie:
                    actions.append(break_tie)
                candidates_to_be_elected.append((candidate, ballots))
        assert len(candidates_to_be_elected) == len(sorted_hopefuls)-len(self.hopefuls)
        
        if candidates_to_be_elected:
            # Elect candidates that met the quota
            for (candidate, ballots) in candidates_to_be_elected:
                actions.append({'elect': candidate, 'transfer': self.elect(candidate, ballots)})
        else:
            # or exclude last place candidate
            (sum_ballots, candidate, ballots, break_tie) = self.next_candidate_to_exclude(sorted_hopefuls)
            if break_tie:
                actions.append(break_tie)
            self.hopefuls.pop(candidate)
            actions.append({'exclude': candidate, 'transfer': self.exclude(candidate, ballots)})
        
        # Check that no one has gone MIA
        assert self.get_candidate_count() == old_candidate_count
        # Check that total ballot tally has not changed
        assertAlmostEqual(self.get_total_ballot_tally(), old_ballot_tally)
        return actions
    
    def run_remaining(self):
        '''Elects the candidate that haven't met the quota while we have room,
        in descending order based on their tallies as long as they have met the 
        minimum required otherwise reject them.
        Returns a list of actions taken
        [
            {'elect': candidate, 'transfer': None},
            or
            {'reject': candidate, 'transfer': None},
            ...
        ]
        '''
        sorted_hopefuls = self.get_sorted_hopefuls()
        actions = []
            
        self.hopefuls.clear()
        for (sum_ballots, candidate, ballots, break_tie) in self.get_top_candidates(sorted_hopefuls):
            if break_tie:
                actions.append(break_tie)
            if sum_ballots >= self.minimum and len(self.elected) < self.num_seats:
                actions.append({'elect': candidate, 'transfer': self.elect(candidate, ballots, transfer_surplus=False)})
            else:
                actions.append({'reject': candidate, 'transfer': self.reject(candidate, ballots)})
            
        return actions
    
    def continue_electing(self):
        '''Returns whether or not more rounds should be run'''
        return len(self.hopefuls)+len(self.elected) > self.num_seats and len(self.elected) < self.num_seats
    
    def still_have_open_seats(self, candidates_to_be_elected):
        return len(self.elected) + len(candidates_to_be_elected) < self.num_seats
        
    def run(self):
        '''Runs the race returning a dictionary of the following structure
        {
            'elected': [{'candidate': candidate, 'ballots_used': {ballot, ...}}, ...],
            'exhausted': {ballot, ...},
            'rounds': [
                {
                    'status': {
                        'elected': [candidate, ...],
                        'excluded': [candidate, ...],
                        'hopefuls': [(candidate, tally) from high tally to lowest], 
                        'quota': quota, 
                        'exhausted': num_exhausted
                    },
                    'actions': [
                        {
                            'break_tie': {candidate, ...}
                        }, ...
                        or
                        {
                            'elect': candidate,
                            'transfer': {'candidates': {candidate: tally}, 'exhausted': tally}
                        }, ...
                        or
                        {
                            'exclude': candidate,
                            'transfer': {...}
                        }, ...
                        or
                        {
                            'reject': candidate,
                            'transfer': None
                        }, ...
                    ]
                },
                ...
            ]
        }
        '''
        self.init_ballots()
        original_ballot_tally = self.get_total_ballot_tally()
        # While we must exclude more candidates, run a round
        while self.continue_electing():
            self.rounds.append({'status': self.get_status(), 'actions': self.run_round()})
        # Elect remaining hopefuls as long as they meet the minimum
        self.rounds.append({'status': self.get_status(), 'actions': self.run_remaining()})
        
        # Check that we have elected at most the number of seats. 
        # Some candidates may have been rejected.
        assert len(self.elected) <= self.num_seats
        # Check that the total tally has not changed
        # despite running the election
        assertAlmostEqual(self.get_total_ballot_tally(), original_ballot_tally)
        
        return {'elected': self.elected, 'exhausted': self.exhausted_ballots, 'rounds': self.rounds}
    
