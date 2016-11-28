import requests

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

CLIENT_ID          = "49d6e5f47163ccd5c6f8"
CLIENT_SECRET      = "6169f791c4b9bc544f11c529de66c82bb94eb20b"
START_REPO         = 1
END_REPO           = 42000000 # This is a good number to make sure that the repository is old enough
REPOSITORY_REQUEST = "https://api.github.com/repositories"

def save_to_file():
    pass
    
def collect_repos():
    repos = {}
    
    i = START_REPO
    while i < END_REPO:
        all_repo_params  = { "since": str(i),
                             "client_id": CLIENT_ID,
                             "client_secret": CLIENT_SECRET }

        temp_repos = requests.get(REPOSITORY_REQUEST, params=all_repo_params).json()
        i = int(temp_repos[len(temp_repos)-1]["id"]) + 1
        for repo in temp_repos:
            repo_params = { "client_id": CLIENT_ID,
                            "client_secret": CLIENT_SECRET }

            # Commits, Collaborators, Contributors, Issues, Branches, Pull, Merges
            # NOTE(Grant): I cannot get collaborators because they are private... however, contributors are not!
            contribs = requests.get(repo["contributors_url"], params=repo_params)
            num_contribs = len(contribs.json())

            # Don't continue if there isn't enough collaborators
            if num_contribs < 3:
                continue

            branches = requests.get(repo["branches_url"], params=repo_params).json()
            # TODO(Grant): Use branches to get all commits
            commits = {}
            
            for branch in branches:
                # NOTE(Grant): Default commits_url -- requests.get(repo["commits_url"], params=repo_params)
                branch_commits = request.get(branch["commit"]["url"], params=repo_params).json()
                
            
            issues   = requests.get(repo["issues_url"], params=repo_params)

            pulls    = requests.get(repo["pulls_url"], params=repo_params)
            langs    = requests.get(repo["languages_url"], params=repo_params)
            merges   = requests.get(repo["merges_url"], params=repo_params)

            for k in range(0, num_collabs):
                pass
            
            repos[repo["id"]] = {
                "html_url": repo["html_url"],
                
            }

def start():
    pass

r = requests.get(REPOSITORY_REQUEST, params={ "since": "40000000", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET })
rjs = r.json()

print(rjs[0])
print("----------------------------------------")
print(rjs[0]["id"])
print(type(rjs))

