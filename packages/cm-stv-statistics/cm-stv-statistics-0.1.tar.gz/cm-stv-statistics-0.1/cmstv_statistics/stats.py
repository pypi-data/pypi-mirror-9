import collections
from pprint import pprint
#The number of #1 choices received by each slate
def numberOfFirstPlaceVotesBySlate(ballots):
    dictFirstPlaceVotesBySlate = {}

    for ballot in ballots:

        if ballot.candidates[0].slate in dictFirstPlaceVotesBySlate:
            dictFirstPlaceVotesBySlate[ballot.candidates[0].slate] += 1
        else:
            dictFirstPlaceVotesBySlate[ballot.candidates[0].slate] = 1

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
        number = len(ballot.candidates)
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
#def voterSatisfaction():
    '''fill this in'''

#The number/percentage of
#def ballotRepresentation():
    '''fill this in'''

#for each winning candidate, the
def slateConstituenciesOfWinners(results,numSeats):
    dictSlateConstituenciesOfWinners = {}

    #for each candidate already elected
    for num in range(0,numSeats):
        candidate = results['elected'][num]['candidate']

        dictCandidateConstituenciesOfWinners = {}

        for ballot in results['elected'][num]['ballots_used']:
            slate = ballot.original_candidates[0].slate
            if slate in dictCandidateConstituenciesOfWinners:
                dictCandidateConstituenciesOfWinners[slate] += ballot.weight
            else:
                dictCandidateConstituenciesOfWinners[slate] = ballot.weight

        dictSlateConstituenciesOfWinners[candidate] = dictCandidateConstituenciesOfWinners

    dictCandidateConstituenciesOfWinners = {}

    for ballot in results['exhausted']:
        slate = ballot.original_candidates[0].slate

        if slate in dictCandidateConstituenciesOfWinners:
            dictCandidateConstituenciesOfWinners[slate] += ballot.weight
        else:
            dictCandidateConstituenciesOfWinners[slate] = ballot.weight

    dictSlateConstituenciesOfWinners['Exhausted'] = dictCandidateConstituenciesOfWinners

    return dictSlateConstituenciesOfWinners



# Below func follows the 'round by round' report - at the end of each outer_forloop...
# it adds each round's winner to candidateConstituenciesOfWinners...
# taking account of each ballot weight and who it goes to per round

def candidateConstituenciesOfWinners(results,numSeats):
    #results is large list of ballot information / numSeats=6
    dictCandidateConstituenciesOfWinners = {}

    counter = 0;
    #print("\ncandidates: ")

    for num in range(0,numSeats):
        candidate = results['elected'][num]['candidate'] #get candidate form elected key's numth index list
        #print(candidate)

        dictOtherCandidateConstituenciesOfWinner = {}

        for ballot in results['elected'][num]['ballots_used']: #get ballot set from the elected key's ballots_used
            # print "\ninner loop"
            counter +=1;

            topCandidate = ballot.original_candidates[0].name

            #if candidate in dict, increase their ballot weight / if not, set it as their ballot weight
            if topCandidate in dictOtherCandidateConstituenciesOfWinner:
                dictOtherCandidateConstituenciesOfWinner[topCandidate] += ballot.weight
            else:
                dictOtherCandidateConstituenciesOfWinner[topCandidate] = ballot.weight

        dictCandidateConstituenciesOfWinners[candidate] = dictOtherCandidateConstituenciesOfWinner
        #print("\ndictCandidateConstituenciesOfWinners")
        #pprint(dictCandidateConstituenciesOfWinners)

    #print("\ncounter")
    #print(counter)
    return dictCandidateConstituenciesOfWinners


def candidateConstituencesOfExhausted(results, candidates, numSeats): #need to find by percentages, not raw numbers
    #candidates parameter is technically the remaining candidates
    # since each round, an original candidate is popped out, we have a rem candidates list here
    # print candidates

# Now we have dictCandidate ready to be scanned --------------------------

    dictExhaustedConstituenciesofWinners = collections.defaultdict(float)

    total=0
    for B in results['exhausted']: #B is the object Ballot at res['ex'], so loop for all Ballot objects
        #total2 += B.weight # total here to get full total, including all candidates
        for candidate in candidates:
            if candidate == (B.original_candidates[0] if B.original_candidates else None):
                #if candidate.name != 'Artem Senchev' and candidate.name != 'Amelia Helland':
                    #excluding Engunia and Nicholas doesn't make a difference - their ballots never went to Exh
                    #here we check the first list item, because that's the one the Ballot goes to
                    dictExhaustedConstituenciesofWinners[candidate] += B.weight
                    total += B.weight #total here to account for ignoring Artem and Amelia


    # DO NOT DELETE BELOW COMMENT - its the method for finding percentages

    # for candidate, eballots in dictExhaustedConstituenciesofWinners.items():
    #     print("\n\npercentages per candidate")
    #     print candidate
    #     print eballots*100/total


    # Functional method:
    # return {
    #     candidate: sum(ballot for ballot in results['exhausted'] if ballot.original_candidates[0] == candidate)
    #     for candidate in candidates
    # }

    return dictExhaustedConstituenciesofWinners


'''ISTHISWORKING?????'''

#def voters grouped by their top choice preference(results):

def ballotCountedAtEndOfElection(results,numSeats):
    dictBallotCountedAtEndOfElection = {}
    dictCandidateTotals = {} #included

    for num in range(0,numSeats):

        for ballot in results['elected'][num]['ballots_used']: # ballot in ballots_used for an elected candidate
            firstChoiceCandidate = ballot.original_candidates[0].name
            ultimateCandidate = results['elected'][num]['candidate'].name

            if firstChoiceCandidate not in dictBallotCountedAtEndOfElection:
                dictBallotCountedAtEndOfElection[firstChoiceCandidate] = {}

                dictCandidateTotals[firstChoiceCandidate] = 0 #included

            if ultimateCandidate in dictBallotCountedAtEndOfElection[firstChoiceCandidate]:
                dictBallotCountedAtEndOfElection[firstChoiceCandidate][ultimateCandidate] += ballot.weight
                #for ex, dict has: Andrea Jao {Exhaust, Engunia..}, Anthony Gil {Amelia, Exhaust...}

                #dictCandidateTotals[firstChoiceCandidate] += ballot.weight #included

                #added below to help with future Exausted vote calculation
                dictBallotCountedAtEndOfElection[firstChoiceCandidate]['Exhausted'] = 0;
            else:
                dictBallotCountedAtEndOfElection[firstChoiceCandidate][ultimateCandidate] = ballot.weight



    for k in dictBallotCountedAtEndOfElection.keys():
        for ballot in results['exhausted']:

            if k in ballot.original_candidates[0].name:

                dictBallotCountedAtEndOfElection[k]['Exhausted'] += ballot.weight
                #for ex, dict['Andrea Jao']['Exhausted'] += ballow.weight


    # DO NOT DELETE BELOW COMMENT - its the method for finding percentages

    for k in dictBallotCountedAtEndOfElection.keys():
        key_total=0
        for v in dictBallotCountedAtEndOfElection[k]:
            key_total += dictBallotCountedAtEndOfElection[k][v] #get its total ballot weight amount

        dictCandidateTotals[k] = key_total

    # print("\nprinting dictCandidateTotals: ")
    # pprint(dictCandidateTotals)

    #now print out the pecentage for each dictCandidateTotals[k][v] by dictBallotCountedAtEndOfElection[k][v]*100/dictCandidateTotals[k]
    for k in dictBallotCountedAtEndOfElection.keys():
        # print("\n----------------") <-- UNCOMMENT THIS LINE(1/3) TO PRINT DESIRED PERCENTAGES
        # print(k) <-- UNCOMMENT THIS LINE(2/3) TO PRINT DESIRED PERCENTAGES
        for v in dictBallotCountedAtEndOfElection[k]:
            percentage = dictBallotCountedAtEndOfElection[k][v]*100/dictCandidateTotals[k]
            # print(v, percentage) <-- UNCOMMENT THIS LINE(3/3) TO PRINT DESIRED PERCENTAGES


    return dictBallotCountedAtEndOfElection
    #dict has original candidates as keys, and a set of elected candidates...
    #showing which how many of the original candidate's ballots went to each elected candidate
    #to include how many of original candidate's ballots went to Exhausted, run over all exhausted ballots...
    #and increment each key's Exhausted value in set of values by that ballot's weight





    '''check this'''

#Shared Slate Support 1
def sharedFirstSlateSupport(ballots):
    dictSharedFirstSlateSupport = {}

    for ballot in ballots:
        #determine slate of number one candidate
        firstSlate = ballot.original_candidates[0].slate

        #determine slate of number two candidate
        if len(ballot.original_candidates) > 1:
            secondSlate = ballot.original_candidates[1].slate
        else:
            secondSlate = 'Exhausted'

        #if first slate in dict
        if firstSlate not in dictSharedFirstSlateSupport:
            dictSharedFirstSlateSupport[firstSlate] = {}

        if secondSlate in dictSharedFirstSlateSupport[firstSlate]:
            dictSharedFirstSlateSupport[firstSlate][secondSlate] += ballot.weight
        else:
            dictSharedFirstSlateSupport[firstSlate][secondSlate] = ballot.weight

    return dictSharedFirstSlateSupport

def exhaustedSecondSlateSupport(dictSharedFirstSlateSupport):

    # dictExhaustedSecondSlateSupport = collections.defaultdict()
    dictExhaustedSecondSlateSupport = {}

    # print("\ntesting dictSharedFirstSlateSupport")
    # for key, value in dictSharedFirstSlateSupport.items():
    #     print(key, value)
    #
    # print("\ntesting individual elements")
    # print(dictSharedFirstSlateSupport['Independent']['Exhausted'])

    dictExhaustedSecondSlateSupport['Independent'] = dictSharedFirstSlateSupport['Independent']['Exhausted']
    dictExhaustedSecondSlateSupport['SMART'] = dictSharedFirstSlateSupport['SMART']['Exhausted']
    dictExhaustedSecondSlateSupport['NOW'] = dictSharedFirstSlateSupport['NOW']['Exhausted']

    total = 0
    for key, val in dictExhaustedSecondSlateSupport.items():
        total += val

    #UNCOMMENT BELOW TWO LINES TO SHOW PERCENTAGES
    #for key, val in dictExhaustedSecondSlateSupport.items():
    #    print '%s %.1f%%' % (key, (val/total*100))

    return dictExhaustedSecondSlateSupport


#Shared Slate Support 2
def sharedSecondSlateSupport(ballots):
    dictSharedSecondSlateSupport = {}

    for ballot in ballots:
        if len(ballot.original_candidates) > 1:
            firstSlate = ballot.original_candidates[0].slate
            secondSlate = ballot.original_candidates[1].slate

            #if first slate in dict
            if secondSlate not in dictSharedSecondSlateSupport:
                dictSharedSecondSlateSupport[secondSlate] = {}

            if firstSlate in dictSharedSecondSlateSupport[secondSlate]:
                dictSharedSecondSlateSupport[secondSlate][firstSlate] += ballot.weight
            else:
                dictSharedSecondSlateSupport[secondSlate][firstSlate] = ballot.weight

    # dictSharedSecondSlateSupport['Exhausted']['NOW'] = dictSharedFirstSlateSupport['NOW']['Exhausted']

    return dictSharedSecondSlateSupport


def sharedFirstCandidateSupport(ballots):
    dictSharedFirstCandidateSupport = {}

    for ballot in ballots:
        firstCandidate = ballot.original_candidates[0].name

        if len(ballot.original_candidates) > 1:
            secondCandidate = ballot.original_candidates[1].name
        else:
            secondCandidate = 'Exhausted'

        if firstCandidate not in dictSharedFirstCandidateSupport:
            dictSharedFirstCandidateSupport[firstCandidate] = {}

        if secondCandidate in dictSharedFirstCandidateSupport[firstCandidate]:
            dictSharedFirstCandidateSupport[firstCandidate][secondCandidate] += ballot.weight
        else:
            dictSharedFirstCandidateSupport[firstCandidate][secondCandidate] = ballot.weight

    return dictSharedFirstCandidateSupport

def sharedSecondCandidateSupport(ballots):
    dictSharedSecondCandidateSupport = {}

    for ballot in ballots:
        if len(ballot.original_candidates) > 1:
            firstCandidate = ballot.original_candidates[0].name
            secondCandidate = ballot.original_candidates[1].name

            if secondCandidate not in dictSharedSecondCandidateSupport:
                dictSharedSecondCandidateSupport[secondCandidate] = {}

            if firstCandidate in dictSharedSecondCandidateSupport[secondCandidate]:
                dictSharedSecondCandidateSupport[secondCandidate][firstCandidate] += ballot.weight
            else:
                dictSharedSecondCandidateSupport[secondCandidate][firstCandidate] = ballot.weight

    return dictSharedSecondCandidateSupport
