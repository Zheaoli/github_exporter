from prometheus_client import Gauge

from github_exporter.config import SETTING, GITHUB_CLIENT, METRIC_REGISTRY

star_gauge = Gauge(
    "github_stars",
    "Number of stars for a repo",
    ["repo_name"],
    registry=METRIC_REGISTRY,
)

fork_gauge = Gauge(
    "github_forks",
    "Number of forks for a repo",
    ["repo_name"],
    registry=METRIC_REGISTRY,
)

issue_metric = Gauge(
    "github_issue",
    "Number of issues for a repo",
    ["repo_name", "issue_state", "issue_title"],
    registry=METRIC_REGISTRY,
)

pr_metric = Gauge(
    "github_pull_request",
    "Number of issues for a repo",
    ["repo_name", "pr_state", "pr_title"],
    registry=METRIC_REGISTRY,
)


def start_github_job():
    for repo_name in SETTING.repo_names:
        start_github_job_for_repo(repo_name)


def start_github_job_for_repo(repo_name):
    # try:
    repo = GITHUB_CLIENT.get_repo(repo_name)

    process_repo_metric(repo_name, repo)
    process_issue_metric(repo_name, repo)
    process_pull_request_metric(repo_name, repo)
    # except Exception as e:
    #     pass


def process_repo_metric(repo_name, repo):
    star_gauge.labels(repo_name).set(repo.stargazers_count)
    fork_gauge.labels(repo_name).set(repo.forks_count)
    # watch_gauge = Gauge("github_watches", "Number of watches for a repo", ["repo_name"], registry=METRIC_REGISTRY,
    #                     _labelvalues=[repo_name])
    # # watch_gauge.set(repo.subscribers_count)


def process_issue_metric(repo_name, repo):
    open_issues = repo.get_issues()
    closed_issues = repo.get_issues(state="closed")
    open_page = open_issues.totalCount // 100 + 2
    close_page = closed_issues.totalCount // 100 + 2
    temp = 1
    while temp <= open_page:
        for issue in open_issues.get_page(temp):
            issue_metric.labels(*[repo_name, issue.state, issue.title]).set(1)
        temp += 1
    temp = 1
    while temp <= close_page:
        for issue in closed_issues.get_page(temp):
            issue_metric.labels(*[repo_name, issue.state, issue.title]).set(1)
        temp += 1


def process_pull_request_metric(repo_name, repo):
    open_prs = repo.get_pulls()
    closed_prs = repo.get_pulls(state="closed")
    open_page = open_prs.totalCount // 100 + 2
    close_page = closed_prs.totalCount // 100 + 2
    temp = 1
    while temp <= open_page:
        for pr in open_prs.get_page(temp):
            pr_metric.labels(*[repo_name, pr.state, pr.title]).set(1)
        temp += 1
    temp = 1
    while temp <= close_page:
        for pr in closed_prs.get_page(temp):
            pr_metric.labels(*[repo_name, pr.state, pr.title]).set(1)
        temp += 1
