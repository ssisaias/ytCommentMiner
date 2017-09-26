import requests
import time
import datetime
import sys
import json

print('Paste down your Oauth API KEY')
oauth = input()
print('Paste down the video id:')
videoId = input()
print('[Info]: Verifying video metadata...', end='\n')

header = {'Authorization': 'Bearer '+oauth}
videopayload =  {'part': 'statistics', 'fields':'items(statistics/commentCount)' , 'id': videoId}

print('')
r = requests.get('https://www.googleapis.com/youtube/v3/videos', videopayload, headers=header)

if r.status_code != 200:
    sys.exit('[Error]: ' + r.text)

commentCount = r.json()['items'][0]['statistics']['commentCount']
if(int(commentCount) > 1000):
    print('Warning: this video contains more than 1k comments, if you wish to cancel press Ctrl+C NOW')
    time.sleep(2)

dumpFile = open('video'+videoId+ datetime.datetime.now().strftime('%Y-%m-%d-%H%M')+'.json', 'w', encoding='utf-8') 
print('[Info]: Obtaining comment threads')
#Get comment Threads

videopayload = ''
videopayload = {'part': 'snippet', 'fields':'items(id,snippet/topLevelComment/snippet/authorDisplayName,snippet/topLevelComment/snippet/textDisplay,snippet/topLevelComment/snippet/textOriginal, snippet/topLevelComment/snippet/publishedAt,snippet/totalReplyCount),pageInfo,nextPageToken' , 'videoId': videoId, 'maxResults': '100'}

threads = {'items': []}

thread_Next_Page_Token_Found = True
while thread_Next_Page_Token_Found:
    r = requests.get('https://www.googleapis.com/youtube/v3/commentThreads', videopayload, headers=header)

    if r.status_code != 200:
        sys.exit('[Error]: ' + r.text)

    #r = open('ff__bkqyjVw2017-09-22-1117.json', 'r', encoding='utf-8')

    top_comment_data = r.json() #json.load(r)
    # print(threads, end='\n')
    for top_level in top_comment_data['items']:
        print('[Info#comment]: Dumping all replies for comment: ' + top_level['id'], end='\n')
        videopayload = {'part': 'snippet', 'fields': 'items(id,snippet/authorDisplayName,snippet/textDisplay,snippet/textOriginal, snippet/publishedAt),pageInfo,nextPageToken','parentId': top_level['id'], 'maxResults': '100'}
        
        if 'replies' not in top_level:
            top_level['replies'] = {'comments':[]}
            
        if 'comments' not in top_level['replies']:
            top_level['replies'] = {'comments':[]}
            
        reply_Next_Page_Token_Found = True
        while reply_Next_Page_Token_Found:
            print('[Info#comment]: retrieving', end='\n')
            r = requests.get('https://www.googleapis.com/youtube/v3/comments', videopayload, headers=header)
            reply_comment_data = r.json()
            
            top_level['replies']['comments'].extend(reply_comment_data['items'])
            if 'nextPageToken' not in reply_comment_data:
                print('[Info#comment]: retrieved last reply page', end='\n')
                reply_Next_Page_Token_Found = False
                continue
            print('[Info]: Next Page Token Found', end='\n')
            videopayload = {'part': 'snippet', 'fields': 'items(id,snippet/authorDisplayName,snippet/textDisplay,snippet/textOriginal, snippet/publishedAt),pageInfo,nextPageToken','parentId': top_level['id'],'pageToken': reply_comment_data['nextPageToken'] , 'maxResults': '100'}
            time.sleep(1)
            pass

    threads['items'].extend(top_comment_data['items'])

    if ('nextPageToken' not in top_comment_data):
        thread_Next_Page_Token_Found = False
        print('[Info#Thread]: retrieved last page', end='\n')
        continue
    print('[Info#Thread]: Next Page Token Found', end='\n')
    videopayload = {'part': 'snippet', 'fields':'items(id,snippet/topLevelComment/snippet/authorDisplayName,snippet/topLevelComment/snippet/textDisplay,snippet/topLevelComment/snippet/textOriginal, snippet/topLevelComment/snippet/publishedAt,snippet/totalReplyCount),pageInfo,nextPageToken' ,'pageToken':top_comment_data['nextPageToken']  , 'videoId': videoId, 'maxResults': '100'}
    time.sleep(1)

dumpFile.write(json.dumps(threads))

dumpFile.close()

r.close()

print('Done.')
    