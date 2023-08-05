"""Calculate a user's activity score
 
Type: personal
 
Input:
    location : /v1/data/tc.you.CompilerTest
    other:	/v1/data/tc.you.ActivityScore
 
Output:
    out1: /v1/data/tc.you.ActivityScore, POST
    out2: /v1/data/tc.you.CompilerTest, PUT
"""
def execute(location, other, *args, **kwargs):
    activityScore = {'name': 'FirstAnswer', 'timestamp' : '2014-08-08T13:14:15Z', 'stringP': 'foo'}
    locationUpdate = {'_id': location[0]['_id'], 'stringP': 'A new value'}
    return dict(out1=[activityScore], out2=[locationUpdate])
