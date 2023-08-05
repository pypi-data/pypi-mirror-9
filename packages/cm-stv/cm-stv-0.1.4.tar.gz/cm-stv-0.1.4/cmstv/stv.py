import re
import json
from models import Candidate, Ballot, Race, assertAlmostEqual

def reset_ballots(ballots):
    '''Resets a set of ballots to their original weight and candidates'''
    for ballot in ballots:
        ballot.reset_weight()
        ballot.reset_candidates()

def run_race(candidates, num_seats, ballots, tie_breakers = None):
    '''Runs a race of candidates for num_seats and ballots.
    Returns dictionary in the format specified by Race.run.
    '''
    reset_ballots(ballots)
    race = Race(candidates=candidates, num_seats=num_seats, ballots=ballots, tie_breakers=tie_breakers)
    return race.run()

def countback(candidates, num_seats, ballots, candidates_resigned, candidates_running=None, tie_breakers = None):
    # Run election
    reset_ballots(ballots)
    race = Race(candidates=candidates, num_seats=num_seats, ballots=ballots, tie_breakers=tie_breakers)
    quota = race.quota
    results = race.run()
    # Build ballots to use for countback from exhausted ballots 
    # and ballots used to elect resigning candidates and count
    # the number of seats required to fill.
    ballots = set(results['exhausted'])
    num_seats = 0
    for elect in results['elected']:
        if elect['candidate'] in candidates_resigned:
            ballots |= elect['ballots_used']
            num_seats += 1
    assertAlmostEqual(sum(ballots), len(candidates_resigned)*quota+sum(results['exhausted']))
    # Build candidates to run in countback if not given
    if not candidates_running:
        elected = set(e['candidate'] for e in results['elected'])
        candidates_running = set(candidates) - elected - candidates_resigned
    # Run countback with minimum equal to half of the quota
    results = Race(candidates=candidates_running, num_seats=num_seats, ballots=ballots, quota=quota, minimum=quota/2.0, tie_breakers=tie_breakers).run()
    return results

def load_blt(file):
    line = next(file)
    (num_candidates, num_seats) = (int(i) for i in line.split())
    
    votes = []
    while True:
        line = next(file)
        if line.startswith('0'):
            break
        else:
            votes.append(int(r) for r in line.split()[1:-1])

    candidate_names_and_slates = []
    name_and_slate_pat = r'"(?P<name>(\\.|[^"\\])*)"(\s+(?P<slate>\d+))?'
    max_slate = 0
    for i in range(num_candidates):
        line = next(file)
        candidate_match = re.search(name_and_slate_pat, line)
        name = candidate_match.group('name').decode('string-escape')
        slate = None
        if candidate_match.group('slate'):
            slate = int(candidate_match.group('slate'))
        max_slate = max(slate, max_slate)
        candidate_names_and_slates.append((name, slate))
    
    slate_pat = r'"(?P<name>(\\.|[^"\\])*)"'
    slates = {}
    for i in range(max_slate):
        slates[i+1] = re.search(slate_pat, next(file)).group('name')

    candidates = {}
    candidates_in_order = []    
    for i, (name, slate) in enumerate(candidate_names_and_slates):
        if slate:
            candidate = Candidate(name=name, slate=slates[slate])
        else:
            candidate = Candidate(name=name)
        candidates[i+1] = candidate
        candidates_in_order.append(candidate)
    
    ballots = set()
    for vote in votes:
        b = Ballot([candidates[r] for r in vote])
        ballots.add(b)
    
    return (num_seats, candidates_in_order, ballots)

def get_blt_lines(num_seats, candidates, ballots, title):
    reset_ballots(ballots)
    candidates = list(candidates)
    candidates_dict = dict((candidate, i+1) for (i, candidate) in enumerate(candidates))
    
    yield '%d %d' % (len(candidates), num_seats)
    
    for ballot in ballots:
        yield ' '.join(['1']+[str(candidates_dict[c]) for c in ballot.candidates]+['0'])
    yield '0'
    
    for candidate in candidates:
        yield json.dumps(str(candidate))
    yield json.dumps(title)
    
def get_pretty_result_lines(results, interactive=False):
    for (i, round) in enumerate(results['rounds']):
        yield '-'*40
        yield '{:^40}'.format('ROUND #%d' % (i+1))
        yield '-'*40
        yield ' %d Seats' % round['status']['num_seats']
        yield ' %d Elected' % len(round['status']['elected'])
        yield ' %d Hopefuls' % len(round['status']['hopefuls'])
        yield ' %d Excluded' % len(round['status']['excluded'])
        yield ' %d Minimum' % round['status']['minimum']
        yield ' %d Quota' % round['status']['quota']
        yield '='*40
        total = round['status']['quota']*len(round['status']['elected'])+round['status']['exhausted']
        yield '%25s: %.2f' % ('Elected', round['status']['quota']*len(round['status']['elected']))
        yield '%25s: %.2f' % ('Exhausted', round['status']['exhausted'])
        for (hopeful, tally) in round['status']['hopefuls']:
            total += tally
            yield '%25s: %.2f' % (hopeful, tally)
        yield '-'*40
        yield '{:^40}'.format('Total: %.2f' % total)
        yield '-'*40
        for action in round['actions']:
            if 'elect' in action:
                yield '{:^40}'.format('**** Elect %s ****' % action['elect'])
                transfer_message = 'Transfer Surplus'
            elif 'exclude' in action:
                yield '{:^40}'.format('xxxx Exclude %s xxxx' % action['exclude'])
                transfer_message = 'Transfer Ballots'
            elif 'reject' in action:
                yield '{:^40}'.format('xxxx Reject %s xxxx' % action['reject'])
            elif 'break_tie' in action:
                yield '-'*40
                yield '| {:^36} |'.format('')
                yield '| {:^36} |'.format('Break Tie')
                yield '| {:^36} |'.format('')
                for c in action['break_tie']:
                    yield '| {:^36} |'.format(str(c))
                yield '| {:^36} |'.format('')
                yield '-'*40
            if 'transfer' in action and action['transfer']:
                yield '> %s:' % transfer_message
                candidate_transfers = action['transfer']['candidates'].items()
                candidate_transfers.sort()
                for (candidate, tally) in candidate_transfers:
                    yield '> %7.2f --> %s' % (tally, candidate)
                yield '> %7.2f --> Exhausted' % (action['transfer']['exhausted'])
        yield '='*40
        if interactive:
            raw_input('{:#^40}'.format(' CONTINUE '))
            yield '\n'
    yield '*'*40
    yield '* {:^36} *'.format('')
    yield '* {:^36} *'.format('WINNERS')
    yield '* {:^36} *'.format('')
    if results['elected']:
        for i, winner in enumerate(results['elected']):
            yield '* #{} {:^33} *'.format(i+1, winner['candidate'])
    else:
        yield '* {:^36} *'.format('None')
    yield '* {:^36} *'.format('')
    yield '*'*40