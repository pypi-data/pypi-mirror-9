"""Calculate a user's activity score
 
Type: personal
 
Input:
    test_data : /v1/data/tc.you.CompilerTest, STREAM
 
Output:
    score_insert: /v1/data/tc.you.ActivityScore, POST
    test_udpate: /v1/data/tc.you.CompilerTest, PUT
"""
def execute(test_data, *args, **kwargs):
    score_insert = kwargs['score_insert']
    test_udpate = kwargs['test_udpate']
    for data in test_data:
        # Update the test data document
        update = {'_id': data['_id'], 'stringP': 'A new value'}
        test_udpate.write(update)

        # Create a new activity score document
        activityScore = {'name': 'FirstAnswer', 'timestamp' : '2014-08-08T13:14:15Z', 
                         'stringP': 'foo'}
        score_insert.write(activityScore)
