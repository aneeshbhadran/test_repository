import requests
from requests.auth import HTTPBasicAuth

JENKINS_URL = '<JENKINS URL>'
JENKINS_FOLDER_NAME = '<FOLDER NAME>'
USERNAME = '<username>'
PASSWORD = '<password>'
CUSTOM_BUILD_JOB_NAME = '<job name>'

job_name_list = list()


def get_all_job_details():
    """
    function to get all the job details
    :return:
    """
    try:
        response = requests.get(
            JENKINS_URL + 'job/' + JENKINS_FOLDER_NAME + '/api/json?tree=jobs[name,url,color]&pretty=true',
            auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            result = response.json()

            for details in result['jobs']:
                if 'color' in details:
                    if details['color'] == 'blue_anime':
                        job_name = details['name']
                        url = details['url']
                        cancel_job(url, job_name)

    except requests.exceptions.RequestException as e:
        print(str(e))
        sys.exit(1)


def cancel_job(url, job_name):
    """
    Function to cancel the build queue
    :param url:
    :param job_name:
    :return:
    """
    try:
        get_job_details = requests.get(url + '/api/json?tree=builds[id,number,result,queueId]',
                                       auth=HTTPBasicAuth(USERNAME, PASSWORD))
    except requests.exceptions.RequestException as e:
        print(str(e))
        sys.exit(1)

    job_details = get_job_details.json()
    if 'builds' in job_details:
        for job_detail in job_details['builds']:
            if job_detail['result'] == 'null':
                job_name_list.append(job_name)
                queue_id = job_detail['queueId']
                print("Canceling job name" + job_name)
                crumber_token = get_crumber_token()
                if crumber_token:
                    requests.post(JENKINS_URL + 'queue/cancelItem?id=' + str(queue_id),
                                  headers={'Jenkins-Crumb': crumber_token},
                                  auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return True


def start_build_job(build_job_name):
    """
    
    :param build_job_name: 
    :return: 
    """""
    print("Starting new build job")
    try:
        crumber_token = get_crumber_token()
        if crumber_token:
            response = requests.post(
                JENKINS_URL + 'job/' + JENKINS_FOLDER_NAME + '/job/' + build_job_name + '/build/',
                headers={'Jenkins-Crumb': crumber_token},
                auth=HTTPBasicAuth(USERNAME, PASSWORD))
            if response.status_code == 201 or 200:
                print("Build triggered successfully!!")
    except requests.exceptions.RequestException as e:
        print(str(e))
        sys.exit(1)


def get_crumber_token():
    """
    Function to get the crumber token
    :return: 
    """
    try:
        get_crumber = requests.get(JENKINS_URL + 'crumbIssuer/api/json', auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if get_crumber.status_code == 200:
            crumber_token = get_crumber.json()['crumb']
            return crumber_token
        return False
    except requests.exceptions.RequestException as e:
        print(str(e))
        sys.exit(1)


def restart_build_jobs():
    """
    Function to restart build job
    :return: 
    """
    for job_name in job_name_list:
        start_build_job(job_name)
    return True


get_all_job_details()
start_build_job(CUSTOM_BUILD_JOB_NAME)
restart_build_jobs()


