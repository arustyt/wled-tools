import json

from git import Repo, GitCommandError

from wled_4_ha import wled_4_ha
from wled_constants import RESULT_KEY, CANDIDATES_KEY, HOLIDAY_KEY, PRESETS_KEY

WLED_HOLIDAY_TOPIC = 'wled/{}/holiday'


def pull_config_repo(config_repo, verbose=False, helper=None):
    if config_repo is not None:
        if verbose:
            helper.log_info("Pulling config repo @ {repo}".format(repo=config_repo))
        try:
            repo = Repo(config_repo)
            origin = repo.remotes.origin
            origin.pull()
        except GitCommandError as gce:
            helper.log_error("Pulling config repo @ {repo} FAILED.".format(repo=config_repo))
            helper.log_error("GitCommandError: {}".format(gce))
    else:
        helper.log_warn("Repo to pull not specified.")


def install_presets_de_jour(job=None, env=None, date_str=None, verbose=False, helper=None):
    if verbose:
        helper.log_info(
            "Calling wled_4_ha({}, {}, {}, {})".format(job, env, date_str, verbose))
    result = wled_4_ha(job_file=job, env=env, date_str=date_str, verbose=verbose)
    process_successful = result[RESULT_KEY]
    return 0 if process_successful else 1


def send_current_holiday_to_ha(job=None, env=None, date_str=None, verbose=False, helper=None, mqttapi=None):
    holidays_only = True
    if verbose:
        helper.log_info(
            "Calling wled_4_ha({}, {}, {}, {}, holidays_only={})".format(job, env, date_str,
                                                                         verbose, holidays_only))
    result = wled_4_ha(job_file=job, env=env, date_str=date_str, verbose=verbose, holidays_only=holidays_only)
    process_successful = result[RESULT_KEY]
    if process_successful:
        send_via_mqtt(candidates=result[CANDIDATES_KEY], holiday_name=result[HOLIDAY_KEY],
                      presets=result[PRESETS_KEY], env=env, mqttapi=mqttapi)
        return 0
    else:
        return 1


def send_via_mqtt(*, candidates, holiday_name, presets, env, mqttapi):
    payload_data = {CANDIDATES_KEY: candidates, HOLIDAY_KEY: holiday_name, PRESETS_KEY: presets}
    payload = json.dumps(payload_data)
    mqttapi.mqtt_publish(WLED_HOLIDAY_TOPIC.format(env), payload=payload)
