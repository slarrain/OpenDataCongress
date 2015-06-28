import json
import csv

dipjson4='diputados_4.json'
votejson4='votations_1282-4982.json'
dipjson5='diputados_5.json'
votejson5='votations_5004-10960.json'
dipjson6='diputados_6.json'
votejson6='votations_11108-19012.json'
dipjson8 = 'diputados_8.json'
votejson8 = 'votations_19192-20702.json'


def party_master_create(leg_period):
    '''
    Given a legislative period, it creates a dictionary with votes as 
    keys, and a dictionary as the value; those dictionaries have parties 
    as keys and the vote breakdown
    It makes the scraped data stored in the JSON files usable for Data 
    Analytics
    '''
    diputados, votations = ret_dict(leg_period) #Reads the json files
    master={}
    for vote in votations.keys():
        master[vote] = {}
        for party in diputados.keys():
            #Initializes the dictionary with empty values
            master[vote][party]={'0':0, '1':0, '2':0, '3':0, '4':0}
        votedic = votations[vote]
        for dipid in votedic.keys():
            party = find_party(dipid,diputados)
            choice = str(votedic[dipid])
            master[vote][party][choice]+=1
    for vote in master.keys():
        for party in master[vote].keys():
            master[vote][party]["total"] = (master[vote][party]["0"]+
                                            master[vote][party]["1"])
            master[vote][party]["not_valid"] = (master[vote][party]["2"] + 
                                                master[vote][party]["3"] +
                                                master[vote][party]["4"])
    return master


def master(leg_period):
    '''
    Given a Legislative Period, creates a dictionary with dipid as keys
    and their score, numbrer of votes they participated, and their 
    loyalty index.
    Details:
        k = number of disloyal votes he participated in.
        3 tentative loyalty indexes: 
            basic = how many times did he voted with the party
            intermediate = mean of scores
            advanced = more complex. index between [(n-k)/n]^2 and (n-k)/n
            But its almost the same as 1-2*(1-basic). So not that useful. 
    We only used votes that were approved with less than 9/10 of support
    to get rid of the junk votes
    '''
    diputados, votations = ret_dict(leg_period)
    party_master = party_master_create(leg_period)
    contested_votes = party_stat_contested(leg_period, party_master)
    index_master = {}
    for party in diputados.keys():
        if big_party(party):
            for dipid in diputados[party]:
                index_master[dipid]={'k':0, 'party': party, 'score':0, 
                                    'num_votes':0, 
                                    'firstname': diputados[party][dipid][0], 
                                    'lastname1': diputados[party][dipid][1], 
                                    'lastname2': diputados[party][dipid][2]}
    for vote in contested_votes:
        for dipid in votations[vote]:
            choice = str(votations[vote][dipid])
            party = find_party(dipid,diputados)
            if big_party(party):
                total_vote = party_master[vote][party]["total"]
                if total_vote == 0:
                    continue
                party_voted_with = (party_master[vote][party][choice]/
                                                    float(total_vote))
                if party_voted_with >= 0.5:
                    score = 1.0
                else:
                    score = party_voted_with
                    index_master[dipid]["k"] = index_master[dipid].get(
                                                "k",0) + 1
                index_master[dipid]["score"] = float(
                                                index_master[dipid].get(
                                                "score",0) + score)
                index_master[dipid]["num_votes"] = index_master[dipid].get(
                                                    "num_votes",0) + 1
    for dipid in index_master.keys():
        n = float(index_master[dipid]["num_votes"])
        k = float (index_master[dipid]['k'])
        score_ad = (index_master[dipid]["score"]-(n-k))/(n-k)
        algorithm = ((n-k)/n)**2+(score_ad*k/n)
        index_master[dipid]["loyalty_basic"] = ((index_master[dipid]["num_votes"]-index_master[dipid]['k'])/float(index_master[dipid]["num_votes"]))
        index_master[dipid]["loyalty_intermediate"] = index_master[dipid]['score']/index_master[dipid]["num_votes"]
        index_master[dipid]["loyalty_advanced"] = algorithm
        #Added this so R could make easier clusterings
        for vote in votations:
            if dipid in votations[vote]:
                if votations[vote][dipid]==0 or votations[vote][dipid]==1:
                    index_master[dipid][vote]=votations[vote][dipid]
                else:
                    index_master[dipid][vote]='NA'
            else:
                index_master[dipid][vote]='NA'
    return index_master

def party_stat_contested(leg_period, party_dic):
    '''
    The dictionary contested_votes is a dictionary that only contains 
    votes that had a winning margin less than some value. 
    For this project, we fixed the value at 0.9
    '''
    diputados, votations = ret_dict(leg_period)
    contested_votes = []
    for vote in party_dic:
        nay = 0
        yay = 0
        total = 0
        for partyid in party_dic[vote]:
            if big_party(partyid):
                nay +=party_dic[vote][partyid]["0"]
                yay +=party_dic[vote][partyid]["1"]
                total+=party_dic[vote][partyid]["0"]
                total+=party_dic[vote][partyid]["1"]
        if abs(nay-yay)/float(total) < 0.9:
            contested_votes.append(vote)
    return contested_votes

# Is it in a big party?
def big_party(party):
    '''
    Small parties with few members were not taken into acount for
    computing the loyalty index for party, because having so little
    representstives, their own vote has too big of an impact, having 
    little meaning
    '''
    #List of the big chilean parties. Unaltered for all 4 periods
    big_parties = ['PS', 'PPD', 'DC', 'UDI', 'RN']
    if party in big_parties:
        return True
    else:
        return False

#Finds the party for a given dipid
def find_party(dipid,diputados):
    for party in diputados.keys():
        if dipid in diputados[party]:
            return party
    return "Not Found"

def ret_dict(leg_period):
    '''
    Rreturns 2 dictionaries: one of diputados and one of votings, 
    for a given period.
    Function used many times through the code.
    '''
    dips = ""
    votes = ""
    if leg_period==4:
        dips = dipjson4
        votes = votejson4
    elif leg_period==5:
        dips = dipjson5
        votes = votejson5
    elif leg_period==6:
        dips = dipjson6
        votes = votejson6
    elif leg_period==8:
        dips = dipjson8
        votes = votejson8
    else:
        return "Error. Bad Period. 4, 5, 6 or 8 are valid"
    with open(dips, 'r') as f:
        diputados = json.load(f)
    with open(votes, 'r') as g:
        votations = json.load(g)
    return diputados, votations

#Change in files


def counts_votes_period (leg_period):
    '''
    Counts the number of representstives who voted for each vote
    that took place in any given period.
    Returns a list with the total number of votes for each voteID
    for for a given period
    '''
    diputados, votings = ret_dict(leg_period)
    count = []
    for voteID in votings:
        count.append(len(votings[voteID]))
    return count


def coalition_master (leg_period):
    '''
    Given a legislative period, it creates a master dictionary for
    computing the Coalition Loyalty Index with all the votes for 
    every VoteID, not by party, but by Coalition.
    It makes the scraped data stored in the JSON files usable for Data 
    Analytics
    '''
    concertacion = ['PS', 'PPD', 'DC', 'IC', 'PRSD']
    alianza = ['UDI', 'RN']
    diputados, votings = ret_dict(leg_period)
    coalition_master = {}
    for voteID in votings:
        coalition_master[voteID] = {}
        coalition_master[voteID]['concertacion']={'0':0, '1':0, '2':0, '3':0, '4':0}
        coalition_master[voteID]['alianza']={'0':0, '1':0, '2':0, '3':0, '4':0}
        for dipID in votings[voteID]:
            x = str(votings[voteID][dipID])
            if find_party(dipID, diputados) in concertacion:
                coalition_master[voteID]['concertacion'][x]+=1
            elif find_party(dipID, diputados) in alianza:
                coalition_master[voteID]['alianza'][x]+=1
        for coalition in coalition_master[voteID]:
            total = 0
            for vote_cod in coalition_master[voteID][coalition]:
                total = total+coalition_master[voteID][coalition][vote_cod]
            coalition_master[voteID][coalition]['total'] = total
            coalition_master[voteID][coalition]['not_valid'] = (total- 
                                    coalition_master[voteID][coalition]['0']-
                                    coalition_master[voteID][coalition]['1'])
    return coalition_master


def coalition_index_loyalty(leg_period):
    '''
    Computes the Loyalty Index for a given Legislative Period, 
    by Coalition. 
    Computes 3 different Loyalty index algorithms. Check the party loyalty 
    index for further documentation.
    Only registers votes with less than 9/10 of aprroval.
    Adds every vote detail, for every representative, with NA if they didn't 
    participated in the vote. This is done for easier clustering on R.
    '''
    diputados, votations = ret_dict(leg_period)
    master_coalition = coalition_master(leg_period)
    coalition_loyalty_index = {}
    dipid_uncoal = []
    for party in diputados.keys():
        for dipid in diputados[party]:
            coalition = find_coalition(dipid, leg_period)
            if coalition:
                coalition_loyalty_index[dipid]={'k':0, 'party':party, 
                                    'coalition': coalition, 
                                    'firstname': diputados[party][dipid][0],
                                    'lastname1': diputados[party][dipid][1], 
                                    'lastname2': diputados[party][dipid][2], 
                                    'score':0, 'num_votes':0}
            else:
                #A party is not in any coalition
                dipid_uncoal.append(dipid) 
    for vote in votations.keys():
        for dipid in votations[vote]:
            choice = str(votations[vote][dipid])
            #Don't waste time analyzing representatives not in a coalition
            if dipid not in dipid_uncoal:
                coalition = coalition_loyalty_index[dipid]['coalition']
                total_vote = master_coalition[vote][coalition]["total"]
                if total_vote == 0:
                    continue
                coal_majority = vote_majority(master_coalition[vote]
                                                        [coalition])
                if coal_majority and coal_majority[1]<0.9:
                    if choice == coal_majority[0]:
                        score = 1.0
                    else:
                        score = 1-coal_majority[1] #Minority percentage
                        coalition_loyalty_index[dipid]["k"] +=1
                    coalition_loyalty_index[dipid]["score"] = (
                                coalition_loyalty_index[dipid]["score"] + 
                                score)
                    coalition_loyalty_index[dipid]["num_votes"] +=1

    for dipid in coalition_loyalty_index.keys():
        n = float(coalition_loyalty_index[dipid]["num_votes"])
        k = float (coalition_loyalty_index[dipid]['k'])
        score_ad = (coalition_loyalty_index[dipid]["score"]-(n-k))/(n-k)
        algorithm = ((n-k)/n)**2+(score_ad*k/n)
        coalition_loyalty_index[dipid]["loyalty_basic"] = (
                (coalition_loyalty_index[dipid]["num_votes"]-
                coalition_loyalty_index[dipid]['k']) / 
                float(coalition_loyalty_index[dipid]["num_votes"]))
        coalition_loyalty_index[dipid]["loyalty_intermediate"] = (
                                coalition_loyalty_index[dipid]['score'] / 
                                coalition_loyalty_index[dipid]["num_votes"])
        coalition_loyalty_index[dipid]["loyalty_advanced"] = algorithm
        #Data added for the R clustering
        for vote in votations:
            if dipid in votations[vote]:
                if votations[vote][dipid]==0 or votations[vote][dipid]==1:
                    coalition_loyalty_index[dipid][vote]=votations[vote][dipid]
                else:
                    coalition_loyalty_index[dipid][vote]='NA'
            else:
                coalition_loyalty_index[dipid][vote]='NA'
    return coalition_loyalty_index


def contested_votes_coalition(leg_period):
    '''
    Given a Legislative Period, it returns a dictionary with the number of
    Unanimous votes for each coalition, the total number of "Unity Votes"
    that happened on that period, and a list with the voteID's.
    A "Unity Vote" is defined as a Vote were the majority of each
    coalition voted differently.
    '''
    coalition_data = coalition_master(leg_period)
    contested_coalition = {'concertacion_unanimous':0, 'unityvotes':0, 
                            'alianza_unanimous':0, 'uv_list':[]}
    for voteID in coalition_data:
        al = vote_majority(coalition_data[voteID]['alianza'])
        con = vote_majority(coalition_data[voteID]['concertacion'])
        if (al and con): #Not a Tie in the coalition
            if al[0]!=con[0]: #If majoritys are different votes (y/n)
                contested_coalition['uv_list'].append(voteID)
                contested_coalition['unityvotes']+=1
                if al[1]==1.0:
                    contested_coalition['alianza_unanimous']+=1
                if con[1]==1.0:
                    contested_coalition['concertacion_unanimous']+=1
    return contested_coalition


def vote_majority (coal_vote):
    '''
    Given a dictionary with the vote details (for a particular voteID, for
    a particular party or coalition) y returns a list with 2 elements:
        [0] -> The Cod how the majority voted.
        [1] -> The percentage of the majoritie
    '''
    vote_majority = []
    if (coal_vote['0']>coal_vote['1']):
        vote_majority.append('0')
    elif (coal_vote['1']>coal_vote['0']):
        vote_majority.append('1')
    else:
        #Tie
        return []
    sub_total = float(coal_vote['0']+coal_vote['1'])
    vote_majority.append((coal_vote[vote_majority[0]]/sub_total))
    return vote_majority


def vote_participation(leg_period):
    '''
    Return a dictionary with the DIPID and the participation percentage, 
    relative to his votes, and relative to all votes on the period.
    '''
    diputados, votings = ret_dict(leg_period)
    vote_participation = {}
    total_votes = 0
    for party in diputados:
        for dipID in diputados[party]:
            vote_participation[dipID] = {'yay_nay':0, 'other_votes':0, 
                                    'party': find_party(dipID, diputados)}
    for voteID in votings:
        total_votes += 1
        for dipID in votings[voteID]:
            if votings[voteID][dipID]==0 or votings[voteID][dipID]==1:
                vote_participation[dipID]['yay_nay']+=1
            else:
                vote_participation[dipID]['other_votes']+=1
    
    for dipID in vote_participation:
        index_participation = (float(vote_participation[dipID]['yay_nay'])/
                                    (vote_participation[dipID]['yay_nay']+
                                    vote_participation[dipID]['other_votes']))
        vote_participation[dipID]['index_participation']=index_participation
        
        #Participation relative to the total votings that took place on period
        relative_participation = (float(vote_participation[dipID]['yay_nay'])/
                                        total_votes)
        vote_participation[dipID]['relative_participation']=relative_participation

    return vote_participation


def contested_votes_per_period(leg_period):
    '''
    Returns an ordered list of the most contested votings in the period
    '''
    coalition_data = coalition_master(leg_period)
    contested_per_period = []
    for voteID in coalition_data:
        al = vote_majority(coalition_data[voteID]['alianza'])
        con = vote_majority(coalition_data[voteID]['concertacion'])
        if (al and con): #Not a Tie in the coalition
            if al[0]!=con[0]: #If majoritys are different votes (y/n)
                dif = abs(al[1]-con[1])
                tup = (dif, voteID)
                contested_per_period.append(tup)
    contested_per_period.sort()
    return contested_per_period 


def contested_vote_party (leg_period):
    '''
    Returns the number of party unanimity in party unity votes and number 
    of party unity votes.                
    '''
    coalition = contested_votes_coalition(leg_period)
    party_master = party_master_create(leg_period)
    #Just the big parties
    parties={"DC":0,"PPD":0, "PS":0,"RN":0,"UDI":0}
    for voteID in coalition['uv_list']:
        for party in parties:
            cod = vote_majority(party_master[voteID][party])
            if cod: #It can return and empty list
                n=(party_master[voteID][party][cod[0]] - 
                    party_master[voteID][party]['total'])
                if n==0: #Unanimous
                    parties[party]+=1
    parties['total'] = coalition['unityvotes']
    return parties

def find_coalition(dipID, leg_period):
    '''
    Given a representstive's ID and a Legislative Period, it returns
    which coalition is he in.
    Returns False if he is in none.
    '''
    concertacion = ['PS', 'PPD', 'DC', 'IC', 'PRSD']
    alianza = ['UDI', 'RN']
    diputados, votings = ret_dict(leg_period)
    for party in diputados:
        if dipID in diputados[party]:
            if party in concertacion:
                return 'concertacion'
            elif party in alianza:
                return 'alianza'
    return False


def loyalty_list (loyalty_dictionary, leg_period, type):
    '''
    Given a Loyalty Index dictionary (coalition or party based) and a 
    Legislative period ID, it creates a list with the names, party and
    index for each representative, and then saves it to a file.
    '''
    n = str(leg_period)
    filename = type+'_loyalty_index_list_'+n+'.csv'
    loy_list = []
    for dipID in loyalty_dictionary:
        data = []
        data.append(loyalty_dictionary[dipID]['lastname1'])
        data.append(loyalty_dictionary[dipID]['lastname2'])
        data.append(loyalty_dictionary[dipID]['firstname'])
        data.append(loyalty_dictionary[dipID]['party'])
        data.append(str("{0:.1f}".format(100*
                        loyalty_dictionary[dipID]['loyalty_basic'])))
        loy_list.append(data)
    loy_list = sorted(loy_list)
    with open (filename, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter = '\t')
        for y in range(0, len(loy_list)):
            csv_writer.writerow([x.encode('utf-8') for x in loy_list[y]])


def do():
    '''
    This do() function executes all the other functions in the program
    and saves the outputs on to several JSON files that are later used
    by the R file to output the graphics.
    '''

    print "Starting Congress Data Analysis file ..."
    
    '''
    Saves a json file with a dictionary. 3 keys, 1 for each period. 
    As values, a list of the number of people who voted on each voting
    File: n_votes.json
    '''
    n_votes = {}
    for x in [4,5,6,8]:
        n_votes[x] = counts_votes_period(x)
    filename = 'n_votes.json'
    with open (filename, 'w') as f:
        json.dump(n_votes, f)
    print 'n_votes 100%'
    
    '''
    3 json files, 1 for each period. vote_participation dictionary in it.
    Files:
        vote_participation_4.json
        vote_participation_5.json
        vote_participation_6.json
        vote_participation_8.json
    '''
    for x in [4,5,6,8]:
        vote_particip = vote_participation(x)
        n = str(x)
        filen = 'vote_participation_'+n+'.json'
        with open (filen, 'w') as g:
            json.dump(vote_particip, g)
        print filen + ' COMPLETED'
    print 'Vote Participation 100%'
    
    '''
    3 json files, 1 for each period. contested_votes_coalition dictionary 
    in it.
    Files:
        coalition_unity_vote_4.json
        coalition_unity_vote_5.json
        coalition_unity_vote_6.json
        coalition_unity_vote_8.json
    '''
    for x in [4,5,6,8]:
        contested_coal = contested_votes_coalition(x)
        n = str(x)
        fil = 'coalition_unity_vote_'+n+'.json'
        with open (fil, 'w') as h:
            json.dump(contested_coal, h)
        print fil + ' COMPLETED'
    print 'Coalition Unity Vote 100%'

    '''
    1 json file with a dictionary, with legislative period ID as keys, 
    and contested_vote_party dictionary as values.
    File:   party_unity_vote.json
    '''
    party_unity = {}
    for x in [4,5,6,8]:
        party_unity[x] = contested_vote_party(x)
    filename = 'party_unity_vote.json'
    with open (filename, 'w') as f:
        json.dump(party_unity, f)
    print 'Party Unity Vote 100%'
    
    '''
    3 json files, 1 for each period. Each outputs the Party Loyalty Index
    of the Master function.
    Files:
        loyalty_index_party_4.json
        loyalty_index_party_5.json
        loyalty_index_party_6.json
        loyalty_index_party_8.json
    '''
    for x in [4,5,6,8]:
        loyalty_index_party = master(x)
        n = str(x)
        fil = 'loyalty_index_party_'+n+'.json'
        open (fil, 'w').write(json.dumps(loyalty_index_party, 
                                        ensure_ascii=False).encode('utf8'))
        loyalty_list(loyalty_index_party, x, 'party')
        print fil + ' and Party Loyalty Index List for Period '+n+' COMPLETED'


    print 'Party Loyalty Index 100%'
    
    '''
    3 json files, 1 for each period. Each outputs the Coalition Loyalty 
    Index dictionary of the coalition_index_loyalty function.
    Files:
        loyalty_index_coalition_4.json
        loyalty_index_coalition_5.json
        loyalty_index_coalition_6.json
        loyalty_index_coalition_8.json
    '''
    for x in [4,5,6,8]:
        loyalty_index_coalition = coalition_index_loyalty(x)
        n = str(x)
        fil = 'loyalty_index_coalition_'+n+'.json'
        open (fil, 'w').write(json.dumps(loyalty_index_coalition, 
                                        ensure_ascii=False).encode('utf8'))
        loyalty_list(loyalty_index_coalition, x, 'coalition')

        print fil + ' and Coalition Loyalty Index List for Period '+n+' COMPLETED'
    print 'Coalition Loyalty Index 100%'
    
    print 'PROGRAM FINISHED'

if __name__ == "__main__":
    do()
    #print 'DO()'