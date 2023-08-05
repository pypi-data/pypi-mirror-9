import collections
from pprint import pprint
#The number of #1 choices received by each slate
def numberOfFirstPlaceVotesBySlate(ballots, slates):
    dictFirstPlaceVotesBySlate = {}

    for ballot in ballots:
        if ballot.original_candidates[0].slate in dictFirstPlaceVotesBySlate:
            dictFirstPlaceVotesBySlate[ballot.original_candidates[0].slate] += 1
        else:
            dictFirstPlaceVotesBySlate[ballot.original_candidates[0].slate] = 1

    return dictFirstPlaceVotesBySlate


#The number of seats obtained by each slate
def numberOfSeatsObtainedBySlate(results):

    dictSeatsObtainedBySlate = {}

    for candidate in results['elected']:
        if candidate['candidate'].slate in dictSeatsObtainedBySlate:
            dictSeatsObtainedBySlate[candidate['candidate'].slate] += 1;
        else:
            dictSeatsObtainedBySlate[candidate['candidate'].slate] = 1;

    return dictSeatsObtainedBySlate

#Number of Choices that Voters Rank
def percentCandidatesRanked(ballots):

    dictNumberOfCandidatesRanked = {}
    dictPercentCandidatesRanked = {}

    #Create dict, key = number of Candidates Ranked, value = number of ballots with that number of candidates ranked
    total = 0.0
    for ballot in ballots:
        number = len(ballot.original_candidates)
        if number in dictNumberOfCandidatesRanked:
            dictNumberOfCandidatesRanked[number] += 1
        else:
            dictNumberOfCandidatesRanked[number] = 1
        total += 1

    avg = 0.0;
    #Created dict, key = number of Candidates Ranked, value = percentage of ballots with that number of candidates ranked
    for number in dictNumberOfCandidatesRanked:
        dictPercentCandidatesRanked[number] = dictNumberOfCandidatesRanked[number]/float(total)
        avg += number * dictNumberOfCandidatesRanked[number]

    #Calculate average number of candidates ranked
    avg = avg / float(total)

    #Calculate median number of candidates ranked
    half = total / 2.0
    checkHalf = 0
    for number in dictNumberOfCandidatesRanked:
        checkHalf += dictNumberOfCandidatesRanked[number]
        if (half < checkHalf):
            median = number
            break
    return (avg,median,dictPercentCandidatesRanked)


#The number/percentage of how many voters had their first choice elected, how many had their second choice elected but not their first, etc.
def voterSatisfaction(ballots, results):
    elected_candidates = [elected['candidate'] for elected in results['elected']] 

    dictVoterSatisfaction = collections.defaultdict(float)
    no_choices_elected = 0.0
    total = 0.0
    
    for ballot in ballots:
        
        found_elected_candidate = False
        for i in range(0,len(ballot.original_candidates)): #only one of these i's will be added to dict
            
            if check_if_candidate_elected(ballot, i, elected_candidates) == True:
                found_elected_candidate = True
                dictVoterSatisfaction[i] += 1
                total += 1
                break # skip to next ballot
        
        if found_elected_candidate == False: #this is a separate measure from the above
            no_choices_elected += 1

    dictVoterSatisfaction[-1] = no_choices_elected
    return dictVoterSatisfaction
        
def check_if_candidate_elected(the_ballot, orig_cand_index, elected_candidates):
    for elected_candidate in elected_candidates:
        if( len(the_ballot.original_candidates) > orig_cand_index):
            if the_ballot.original_candidates[orig_cand_index] == elected_candidate:
                return True
    return False


#The number/percentage of
def ballotRepresentation(ballots, results):
    
    dictBallotRepresentation = collections.defaultdict(float)
        
    for elected in results['elected']:
        for ballot_used in elected['ballots_used']:
            
            for j in range(0, len(ballot_used.original_candidates)):
                if ballot_used.original_candidates[j] == elected['candidate']:
                    dictBallotRepresentation[j] += ballot_used.weight
                    
    counted_for_none = 0
    for exhausted_ballot in results['exhausted']:
        counted_for_none += exhausted_ballot.weight
    dictBallotRepresentation[-1] = counted_for_none
    return dictBallotRepresentation

#for each winning candidate, the
def slateConstituenciesOfWinners(results):
    dictSlateConstituenciesOfWinners = {}

    #for each candidate already elected
    for elected in results['elected']:
        candidate = elected['candidate']

        dictCandidateConstituenciesOfWinners = {}

        for ballot in elected['ballots_used']:
            slate = ballot.original_candidates[0].slate
            if slate in dictCandidateConstituenciesOfWinners:
                dictCandidateConstituenciesOfWinners[slate] += ballot.weight
            else:
                dictCandidateConstituenciesOfWinners[slate] = ballot.weight

        dictSlateConstituenciesOfWinners[candidate] = dictCandidateConstituenciesOfWinners

    constituenciesOfExhausted = {}

    for ballot in results['exhausted']:
        slate = ballot.original_candidates[0].slate

        if slate in constituenciesOfExhausted:
            constituenciesOfExhausted[slate] += ballot.weight
        else:
            constituenciesOfExhausted[slate] = ballot.weight

    return dictSlateConstituenciesOfWinners, constituenciesOfExhausted


# Below func follows the 'round by round' report - at the end of each outer_forloop...
# it adds each round's winner to candidateConstituenciesOfWinners...
# taking account of each ballot weight and who it goes to per round

def candidateConstituenciesOfWinners(results):
    dictCandidateConstituenciesOfWinners = {}

    for elected in results['elected']:
        candidate = elected['candidate']

        dictOtherCandidateConstituenciesOfWinner = {}

        for ballot in elected['ballots_used']: #get ballot set from the elected key's ballots_used
            topCandidate = ballot.original_candidates[0]

            if topCandidate in dictOtherCandidateConstituenciesOfWinner:
                dictOtherCandidateConstituenciesOfWinner[topCandidate] += ballot.weight
            else:
                dictOtherCandidateConstituenciesOfWinner[topCandidate] = ballot.weight

        dictCandidateConstituenciesOfWinners[candidate] = dictOtherCandidateConstituenciesOfWinner

    constituenciesOfExhausted = collections.defaultdict(float)

    for ballot in results['exhausted']:
        constituenciesOfExhausted[ballot.original_candidates[0]] += ballot.weight

    return dictCandidateConstituenciesOfWinners, constituenciesOfExhausted

def candidateConstituencesOfExhausted(results, candidates, numSeats): 
    #candidates is technically the remaining candidates

    candidateConstituencesOfExhausted = collections.defaultdict(float)

    for B in results['exhausted']:     
        for candidate in candidates:
            if candidate == (B.original_candidates[0] if B.original_candidates else None):
                    candidateConstituencesOfExhausted[candidate] += B.weight 

    return candidateConstituencesOfExhausted


#def voters grouped by their top choice preference(results):
def ballotCountedAtEndOfElection(results,numSeats):
    dictBallotCountedAtEndOfElection = collections.defaultdict(lambda: collections.defaultdict(int)) 
    dictCandidateTotals = {}

    for num in range(0,numSeats):

        for ballot in results['elected'][num]['ballots_used']: # ballot in ballots_used for an elected candidate
            firstChoiceCandidate = ballot.original_candidates[0]
            ultimateCandidate = results['elected'][num]['candidate']

            if firstChoiceCandidate not in dictBallotCountedAtEndOfElection:
                dictCandidateTotals[firstChoiceCandidate] = 0

            dictBallotCountedAtEndOfElection[firstChoiceCandidate][ultimateCandidate] += ballot.weight

    for k in dictBallotCountedAtEndOfElection.keys():
        for ballot in results['exhausted']:
            if k == ballot.original_candidates[0]:
                dictBallotCountedAtEndOfElection[k]['Exhausted'] += ballot.weight


    return dictBallotCountedAtEndOfElection
    #dict has original candidates as keys, and a set of elected candidates...
    #showing which how many of the original candidate's ballots went to each elected candidate
    #to include how many of original candidate's ballots went to Exhausted, run over all exhausted ballots...
    #and increment each key's Exhausted value in set of values by that ballot's weight


    '''check this'''

#Shared Slate Support 1
def sharedFirstSlateSupport(ballots):
    dictSharedFirstSlateSupport = collections.defaultdict(
            lambda: collections.defaultdict(int)) 

    for ballot in ballots:
        #determine slate of number one candidate
        firstSlate = ballot.original_candidates[0].slate

        #determine slate of number two candidate
        if len(ballot.original_candidates) > 1:
            secondSlate = ballot.original_candidates[1].slate
        else:
            secondSlate = 'Exhausted'

        dictSharedFirstSlateSupport[firstSlate][secondSlate] += 1

    return dictSharedFirstSlateSupport

#Shared Slate Support 2
def sharedSecondSlateSupport(ballots):
    dictSharedSecondSlateSupport = collections.defaultdict(
            lambda: collections.defaultdict(int))

    for ballot in ballots:
        if len(ballot.original_candidates) > 1:
            firstSlate = ballot.original_candidates[0].slate
            secondSlate = ballot.original_candidates[1].slate

            dictSharedSecondSlateSupport[secondSlate][firstSlate] += 1

    return dictSharedSecondSlateSupport


def sharedFirstCandidateSupport(ballots):
    dictSharedFirstCandidateSupport = collections.defaultdict(
            lambda: collections.defaultdict(int))

    for ballot in ballots:
        firstCandidate = ballot.original_candidates[0]

        if len(ballot.original_candidates) > 1:
            secondCandidate = ballot.original_candidates[1]
        else:
            secondCandidate = 'Exhausted'

        dictSharedFirstCandidateSupport[firstCandidate][secondCandidate] += 1

    return dictSharedFirstCandidateSupport

def sharedSecondCandidateSupport(ballots):
    dictSharedSecondCandidateSupport = collections.defaultdict(
            lambda: collections.defaultdict(int))

    for ballot in ballots:
        if len(ballot.original_candidates) > 1:
            firstCandidate = ballot.original_candidates[0]
            secondCandidate = ballot.original_candidates[1]

            dictSharedSecondCandidateSupport[secondCandidate][firstCandidate] += 1

    return dictSharedSecondCandidateSupport
