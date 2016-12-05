import sys
import time
from datetime import datetime
import requests

# curl -i "https://api.github.com/users/whatever?client_id=49d6e5f47163ccd5c6f8&client_secret=6169f791c4b9bc544f11c529de66c82bb94eb20b"
#
# Repo CSV Format:
#    Repo ID, Number of Contributors, Number of Commits, Number of Branches, Number of Pulls,
#    Number of Languages, Number of Issues, Number of Merges, Language CSV, Contributor CSV, Commits CSV
#    
# Language CSV Format:
#    Language Name, Number of Bytes
#
# Contributor CSV Format:
#    Contributor ID, ????
#
# Commits CSV Format:
#    Commit SHA, Commit Author (ID?), Commit Date,

CLIENT_ID     = "49d6e5f47163ccd5c6f8"
CLIENT_SECRET = "6169f791c4b9bc544f11c529de66c82bb94eb20b"
START_REPO    = 0
END_REPO      = 42000000 # This is a good number to make sure that the repository is old enough
BASE_URL      = "https://api.github.com/"
BASE_PARAMS   = { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET }
TIME          = 0
CURRENT_ID    = 1500

def create_repo_csv():
    print("CREATED repo.csv\n")
    save_to_file("repos.csv", "repo_id,num_contribs,num_commits,num_branches,num_pulls,num_langs,num_issues,num_merges,lang_csv,contrib_csv,commits_csv\n")

def save_to_file(file_name, data):
    file_handler = open(file_name, 'a')
    file_handler.write(data)

    file_handler.close()

def check_rate_limit():
    r = requests.get(BASE_URL+"rate_limit", params=BASE_PARAMS).json()

    return int(r["rate"]["remaining"])

def make_request(i, url, parameters):
    can_continue = False
    r = None
    while not can_continue:
        r = requests.get(url, params=parameters)
        if r.status_code == 403:
            print("Hit limit at: " + str(datetime.now()) + "\n")
            print("At temp_repos of start id: " + str(i) + "\n")
            print("Current number of repos collected: " + str(num_repos))
            time.sleep(4000)
        else:
            can_continue = True

    return r
        
def collect_repos():
    num_repos = 0
    all_repo_params = {}
    repo_params = {}
    branch_params = {}
    for key,value in BASE_PARAMS.items():
        all_repo_params[key] = value
        repo_params[key] = value
        branch_params[key] = value

    TIME = time.time()
    print("BEGIN\n")
    
    # Go through all the public repos starting from START_REPO and ending with END_REPO, 100 repos at a time
    i = CURRENT_ID
    last_i = CURRENT_ID
    while i < END_REPO:
        all_repo_params["since"] = str(i)

        can_continue = False
        temp_repos = None
        while not can_continue:
            temp_repos = requests.get(BASE_URL+"repositories", params=all_repo_params)

            if temp_repos.status_code == 403 and check_rate_limit() == 0:
                print("Hit limit at: " + str(datetime.now()) + "\n")
                print("At temp_repos of start id: " + str(i) + "\n")
                print("Current number of repos collected: " + str(num_repos))
                time.sleep(4000)
            else:
                can_continue = True
        temp_repos = temp_repos.json()

        if temp_repos[0]["id"] < CURRENT_ID:
            print(temp_repos[0]["id"])
            print("Finished with i: ", i)
            print('\n')
            print("Somehow looped back around!")
            sys.exit(0)

        if temp_repos[0]["id"] < last_i:
            print(temp_repos[0]["id"])
            print("Finished with i: ", i)
            print('\n')
            print("Somehow looped back around!")
            sys.exit(0)

        if time.time() - TIME > 20:
            print("\n------------------------------------------------\n")
            print("            CURRENT STATUS\n")
            print("NUMBER OF REPOS: " + str(num_repos) + "\n")
            print("CURRENT i: " + str(i) + "\n")
            TIME = time.time()
            
        # Go through the 100 repos
        for repo in temp_repos:
            langs_csv = "csvFiles\\" + str(repo["id"]) + "-lang.csv"
            contribs_csv = "csvFiles\\" + str(repo["id"]) + "-contribs.csv"
            commits_csv = "csvFiles\\" + str(repo["id"]) + "-commits.csv"
            repo_csv = "repos.csv"
            
            csv_sep = ","

            #####
            ### CONTRIBUTORS
            #####
            can_continue = False
            contribs = None
            while not can_continue:
                contribs = requests.get(repo["contributors_url"], params=repo_params)

                if contribs.status_code is not 200 and check_rate_limit() == 0:
                    print("Hit limit at: " + str(datetime.now()) + "\n")
                    print("At contribs of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                    print("Current number of repos collected: " + str(num_repos))
                    time.sleep(4000)
                else:
                    can_continue = True
            if contribs.status_code is not 200:
                continue                    
            contribs = contribs.json()
            num_contribs = len(contribs)

            # Don't continue if there isn't enough collaborators
            if num_contribs < 3:
                continue

            contribs_csv_info = "contrib_id,contrib_login,num_contributions\n"
            for contrib in contribs:
                contribs_csv_info += csv_sep.join((str(contrib["id"]), str(contrib["login"]), str(contrib["contributions"]))) + '\n'

            #####
            ### BRANCHES
            #####
            can_continue = False
            branches = None
            while not can_continue:
                branches = requests.get(repo["branches_url"].rsplit("{",1)[0], params=repo_params)

                if branches.status_code is not 200 and check_rate_limit() == 0:
                    print("Hit limit at: " + str(datetime.now()) + "\n")
                    print("At branches of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                    print("Current number of repos collected: " + str(num_repos))
                    time.sleep(4000)
                else:
                    can_continue = True
            if branches.status_code is not 200:
                continue
            branches = branches.json()
            num_branches = len(branches)

            #print('************\n')
            #print(branches)
            #print('\n')
            #print('************\n')
            #####
            ### COMMITS
            #####            
            commits_csv_info = "sha,committer_id,date\n"
            num_commits = 0
            for branch in branches:
                #print('-------------\n')
                #print(branch)
                #print('\n')
                #print('-------------\n')
                branch_params["sha"] = branch["commit"]["sha"]
                branch_params["per_page"] = 1000000
                
                # NOTE(Grant): Default commits_url -- requests.get(repo["commits_url"], params=repo_params)
                can_continue = False
                branch_commits = None
                while not can_continue:
                    #print(repo["url"]+"/commits\n")
                    #print(branch_params)
                    #print('\n')
                    branch_commits = requests.get(repo["url"]+"/commits", params=branch_params)

                    if branch_commits.status_code is not 200 and check_rate_limit() == 0:
                        print("Hit limit at: " + str(datetime.now()) + "\n")
                        print("At branch_commits of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                        print("Current number of repos collected: " + str(num_repos))
                        time.sleep(4000)
                    else:
                        can_continue = True
                #print(branch_commits)
                #print('\n')
                if branch_commits.status_code is not 200:
                    continue
                branch_commits = branch_commits.json()

                #print(branch_commits)
                #print('\n')
                for commit in branch_commits:
                    committer_id = commit["committer"]

                    if committer_id is None:
                        committer_id = "?"
                    else:
                        committer_id = committer_id["id"]
                        
                    commits_csv_info += csv_sep.join((str(commit["sha"]), str(committer_id), commit["commit"]["committer"]["date"])) + '\n'
                    num_commits += 1

            #####
            ### LANGUAGES
            #####
            can_continue = False
            langs = None
            while not can_continue:
                langs = requests.get(repo["languages_url"], params=repo_params)

                if langs.status_code is not 200 and check_rate_limit() == 0:
                    print("Hit limit at: " + str(datetime.now()) + "\n")
                    print("At langs of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                    print("Current number of repos collected: " + str(num_repos))
                    time.sleep(4000)
                else:
                    can_continue = True
            if langs.status_code is not 200:
                continue                    
            langs = langs.json()
                
            num_langs = len(langs)

            langs_csv_info = "language_name,num_bytes\n"
            for lang, num_bytes in langs.items():
                langs_csv_info += csv_sep.join((lang, str(num_bytes))) + '\n'

            #####
            ### ISSUES, PULLS, MERGES
            #####
            can_continue = False
            issues = None
            while not can_continue:
                issues = requests.get(repo["issues_url"].rsplit("{",1)[0], params=repo_params)

                if issues.status_code is not 200 and check_rate_limit() == 0:
                    print("Hit limit at: " + str(datetime.now()) + "\n")
                    print("At issues of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                    print("Current number of repos collected: " + str(num_repos))
                    time.sleep(4000)
                else:
                    can_continue = True
            if issues.status_code is not 200:
                continue
            num_issues = len(issues.json())
            
            can_continue = False
            pulls = None
            while not can_continue:
                pulls = requests.get(repo["pulls_url"].rsplit("{",1)[0], params=repo_params)

                if pulls.status_code is not 200 and check_rate_limit() == 0:
                    print("Hit limit at: " + str(datetime.now()) + "\n")
                    print("At pulls of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                    print("Current number of repos collected: " + str(num_repos))
                    time.sleep(4000)
                else:
                    can_continue = True
            if pulls.status_code is not 200:
                continue                    
            num_pulls = len(pulls.json())

            can_continue = False
            while not can_continue:
                merges = requests.get(repo["merges_url"], params=repo_params)
                print(merges.status_code)
                if merges.status_code is not 200 and check_rate_limit() == 0:
                    print("Hit limit at: " + str(datetime.now()) + "\n")
                    print("At merges of start id: " + str(i) + " and current id of: " + str(repo["id"]) + "\n")
                    print("Current number of repos collected: " + str(num_repos))
                    time.sleep(4000)
                else:
                    can_continue = True
            if merges.status_code is not 200:
                continue
            num_merges = len(merges.json())

            repo_info_csv = csv_sep.join((str(repo["id"]), str(num_contribs), str(num_commits), str(num_branches), str(num_pulls),
                                     str(num_langs), str(num_issues), str(num_merges), langs_csv, contribs_csv, commits_csv)) + '\n'

            print("end\n")
            save_to_file(contribs_csv, contribs_csv_info)
            save_to_file(commits_csv, commits_csv_info)
            save_to_file(langs_csv, langs_csv_info)
            save_to_file(repo_csv, repo_info_csv)
            num_repos += 1

        last_i = i
        i = int(temp_repos[len(temp_repos)-1]["id"]) + 1

    print("END\n")

#create_repo_csv()
collect_repos()
