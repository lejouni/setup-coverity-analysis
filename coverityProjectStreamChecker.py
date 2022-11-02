import requests
import argparse
import sys
import logging
from timeit import default_timer as timer


__author__ = "Jouni Lehto"
__versionro__="0.1.1"

def createStream(streamName, projectName):
    logging.debug(f'Stream with name: {streamName} did not exists -> creating it' )
    params={
        "description": "Stream created via API",
        "name": streamName,
        "primaryProjectName": projectName,
        "triageStoreName": "Default Triage Store",
        "versionMismatchMessage": "null"
    }
    headers = {'Accept': 'application/json'}
    endpoint = f'/api/v2/streams?locale=en_us'
    r = requests.post(args.coverity_url + endpoint, headers=headers, auth=(args.username, args.password), json=params)
    if( r.status_code == 201 ):
        logging.debug(f'Stream with name {streamName} is created.')
    else:
        raise SystemExit(f'Stream creation with name {streamName} failed!, error: {r.content}')

def createProject(projectName):
    logging.debug(f'Project with name {projectName} did not exists -> creating it')
    params={
        "description": "Project created via API",
        "name": projectName,
        "roleAssignments": [],
        "streamLinks": [],
        "streams": []
    }
    headers = {'Accept': 'application/json'}
    endpoint = f'/api/v2/projects?locale=en_us'
    r = requests.post(args.coverity_url + endpoint, headers=headers, auth=(args.username, args.password), json=params)
    if( r.status_code == 201 ):
        logging.debug(f'Project with name {projectName} is created.')
    else:
        raise SystemExit(f'Project creation with name {projectName} failed!, error: {r.content}')


#
# Get proejct name for the given stream. Use Coverity API endpoint (/api/v2/streams/).
#
def isStream(streamName):
    headers = {'Accept': 'application/json'}
    endpoint = f'/api/v2/streams/{streamName}?locale=en_us'
    r = requests.get(args.coverity_url + endpoint, headers=headers, auth=(args.username, args.password))
    if( r.status_code == 404 ):
        return False
    elif( r.status_code == 200 ):
        return True
    else:
        raise SystemExit(f'Stream request failed!, error: {r.content}')

#
# Get the projectID with the given project name. Use Coverity API endpoint (/api/v2/projects/)
#
def isProject(project_name):
    headers = {'Accept': 'application/json'}
    endpoint = f'/api/v2/projects/{project_name}?includeChildren=false&includeStreams=false&locale=en_us'
    r = requests.get(args.coverity_url + endpoint, headers=headers, auth=(args.username, args.password))
    if( r.status_code == 404 ):
        return False
    elif( r.status_code == 200 ):
        return True
    else:
        raise SystemExit(f'Project request failed!, error: {r.content}')


#
# Main mathod
#
if __name__ == '__main__':
    start = timer()
    result = False
    parser = argparse.ArgumentParser(
        description="Coverity Project and Stream Checker"
    )
    #Parse commandline arguments
    parser.add_argument('--coverity_url', help="Coverity URL.", default="", required=True)
    parser.add_argument('--project_name', help="Coverity project name.", default="", required=True)
    parser.add_argument('--stream_name', help="Coverity stream name.", default="", required=True)
    parser.add_argument('--password', help='User password for Coverity', default="", required=True)
    parser.add_argument('--username', help='Username for Coverity', default="", required=True)
    parser.add_argument('--log_level', help="Will print more info... default=INFO", default="INFO")
    
    args = parser.parse_args()
    #Initializing the logger
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(module)s: %(message)s', stream=sys.stderr, level=args.log_level)
    #Printing out the version number
    logging.info("Coverity Project and Stream Checker version: " + __versionro__)
    #Creating project if it is not existing yet
    if not isStream(args.stream_name):
        if not isProject(args.project_name):
            createProject(args.project_name)
        else:
            logging.debug(f'Project with name {args.project_name} exists -> no need to create!')
        createStream(args.stream_name, args.project_name)
    else:
        logging.debug(f'Stream with name {args.stream_name} exists -> no need to create!')
    if(logging.getLogger().isEnabledFor(logging.INFO)):
        end = timer()
        logging.info(f"Checking took: {end - start} seconds.")
