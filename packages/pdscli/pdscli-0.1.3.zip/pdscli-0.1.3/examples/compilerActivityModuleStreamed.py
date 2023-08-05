"""Calculate a user's activity score
 
Type: personal
 
Input:
    location : /v1/data/tc.you.CompilerTest, STREAM
 
Output:
    out1: /v1/data/tc.you.ActivityScore, POST
"""
def execute(location, *args, **kwargs):
    out1 = []
    for loc in location:
        out1.append({'name': 'FirstAnswer', 'timestamp' : '2014-08-08T13:14:15Z', 'stringP': 'foo'})
    return dict(out1=out1)
