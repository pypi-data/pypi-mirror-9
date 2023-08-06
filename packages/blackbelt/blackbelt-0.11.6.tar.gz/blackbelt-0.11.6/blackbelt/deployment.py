from subprocess import check_call

from blackbelt.handle_github import get_current_branch
from blackbelt.hipchat import post_message


def deploy_staging():
    branch_name = get_current_branch()

    post_message("@here Deploying branch %s to staging" % branch_name)

    check_call(['grunt', 'deploy', '--app=apiary-staging', '--force', "--branch=%s" % branch_name])
