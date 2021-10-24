from loguru import logger
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
    ["repo_name", "issue_state", "issue_title", "label"],
    registry=METRIC_REGISTRY,
)

pr_metric = Gauge(
    "github_pull_request",
    "Number of issues for a repo",
    ["repo_name", "pr_state", "pr_title", "label"],
    registry=METRIC_REGISTRY,
)

watch_gauge = Gauge(
    "github_watches",
    "Number of watches for a repo",
    ["repo_name"],
    registry=METRIC_REGISTRY,
)


def start_github_job():
    start_github_job_for_repo(SETTING.repo_name)


def start_github_job_for_repo(repo_name):
    try:
        repo = GITHUB_CLIENT.get_repo(repo_name)
        process_repo_metric(repo_name, repo)
        process_issue_metric(repo_name, repo)
        process_pull_request_metric(repo_name, repo)
    except Exception as e:
        logger.exception(e)


def process_repo_metric(repo_name, repo):
    star_gauge.labels(repo_name).set(repo.stargazers_count)
    fork_gauge.labels(repo_name).set(repo.forks_count)
    watch_gauge.labels(repo_name).set(repo.subscribers_count)


def process_issue_metric(repo_name, repo):
    all_issues = repo.get_issues(state="all")
    all_pages = all_issues.totalCount // 30 + 2
    temp = 0
    while temp <= all_pages:
        for issue in all_issues.get_page(temp):
            if issue.pull_request:
                continue
            issue_metric.labels(*[repo_name, issue.state, issue.title, "None"]).set(1)
            if issue.labels:
                for label in issue.labels:
                    issue_metric.labels(
                        *[repo_name, issue.state, issue.title, label.name]
                    ).set(1)
        temp += 1


def process_pull_request_metric(repo_name, repo):
    closed_prs = repo.get_pulls(state="all")
    all_pages = closed_prs.totalCount // 100 + 2
    temp = 0
    while temp <= all_pages:
        for pr in closed_prs.get_page(temp):
            pr_metric.labels(*[repo_name, pr.state, pr.title, "None"]).set(1)
            if pr.labels:
                for label in pr.labels:
                    pr_metric.labels(*[repo_name, pr.state, pr.title, label.name]).set(1)
        temp += 1
