from xmlrpc.client import DateTime
from firebase_admin import firestore
from datetime import datetime

def getUser(uid):
    data = firestore.client().collection('Users').document(uid).get().to_dict()
    refers = []
    for d in data['referals']:
        ur = firestore.client().collection('Users').document(d['id']).get().to_dict()
        refers.append({'name' : ur['name'], 'id':ur['id'] ,'prize' :d['prize'] })
    data['referals'] = refers
    return data


def getLevelUpRequirement(level):

    return firestore.client().collection('level-up-requirement').document(str(level)).get().to_dict()

def myMax(list1):
 
    # Assume first number in list is largest
    # initially and assign it to variable "max"
    max = list1[0]
 # Now traverse through the list and compare
    # each number with "max" value. Whichever is
    # largest assign that value to "max'.
    for x in list1:
        if x > max :
             max = x
     
    # after complete traversing the list
    # return the "max" value
    return max


def getTurnaments(id):
    data = {}
    scores = [0,1]
    parties = []
    participant_score = 0  # str(datetime.now().strftime("%Y:%m:%d")) 2022:08:11
    response = firestore.client().collection('turnaments').document(str(datetime.now().strftime("%Y:%m:%d"))).get().to_dict()
    
    for i in response['participants']:
        scores.append(i['score'])
        print(i)
        if i['user'] == id:
            participant_score = i['score']
            data['participant_array_id'] = {
                'user' : id,
                'score': i['score'],
            }

    data['participants_score'] = participant_score
    
    data['prize'] = response['prize']
    data['leaderboard'] = sorted(response['participants'], key=lambda x: x['score'])
    data['leaderboard'].reverse()
    data['highest_score'] = myMax(scores)
    for u in range(len(response['participants'])):
        parties.append(data['leaderboard'][u])
        data['leaderboard'][u]['id'] = data['leaderboard'][u]['user']
        data['leaderboard'][u]['user'] = getUser(data['leaderboard'][u]['user'])['name']
    data['participants_notSirialized'] = parties
    print(datetime.now().strftime("%Y:%m:%d"))
    print(parties)
    return data


def levelUp(score,current_level,uid):
    levelupReq = getLevelUpRequirement(current_level)
    user = getUser(str(uid))
    if score >= levelupReq['score']:
        firestore.client().collection('Users').document(str(uid)).update({
            'level' : levelupReq['level-upgraded'],
            'earning' : user['earning'] + levelupReq['prize']
        })
        
        
        
def getAllUsers():
    serialized = []
    users = firestore.client().collection('Users').get()
    for u in users:
        serialized.append(u.to_dict())
    return serialized

def getTurnamentsForAdmin():
    serialized = []
    
    turnaments = firestore.client().collection('turnaments').get()
    for u in turnaments:
        serialized.append(u.to_dict())
        
    for p in serialized:
        scores = [0]
        
        for i in p['participants']:
            scores.append(i['score'])
        if len(p['participants'])  > 0:
            p['highest_score_holder'] = sorted(p['participants'], key=lambda x: x['score'])[0]['user']
            p['highest_score_holder'] = getUser(p['highest_score_holder'])['name']
        p['highest_score'] = myMax(scores)
        p['participants_len'] = len(p['participants'])
        
    
    return serialized
    

def getLevelsForAdmin():
    
    serialized = []
    levels = firestore.client().collection('level-up-requirement').get()
    for u in levels:
        serialized.append(u.to_dict())
    return serialized


def getReferalsForAdmin():
    serialized = []
    users = firestore.client().collection('ReferalsRequest').get()
    index = 0
    for u in users:
        serialized.append(u.to_dict())
        serialized[index]['id']= u.id
        index = index + 1
    return serialized

def getWithdrawlsForAdmin():
    serialized = []
    withdrawls = firestore.client().collection('withdrawls').get()
    index = 0
    for u in withdrawls:
        
        serialized.append(u.to_dict())
        serialized[index]['id']= u.id
        index = index + 1
   
        
    
    print(serialized)
    return serialized

def checkIp(ip):
    isAlreadyUser = False
    data = firestore.client().collection('Ip Address').document('Ip Address').get().to_dict()['Ip']
    if ip != None:
        for i in data:
            if i == ip:
                isAlreadyUser = True
    else:
        isAlreadyUser = True
    
    return isAlreadyUser
