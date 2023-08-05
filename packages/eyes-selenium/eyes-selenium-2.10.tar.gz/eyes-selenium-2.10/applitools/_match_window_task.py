import functools
import time
from struct import pack

from ._webdriver import EyesScreenshot


# noinspection PyProtectedMember
from applitools import logger
from applitools.utils import general_utils


class MatchWindowTask(object):
    """
    Handles matching of output with the expected output (including retry and 'ignore mismatch'
    when needed).
    """
    _MATCH_INTERVAL = 0.5

    def __init__(self, eyes, agent_connector, running_session, driver, default_retry_timeout):
        self._eyes = eyes
        self._agent_connector = agent_connector
        self._running_session = running_session
        self._driver = driver
        self._default_retry_timeout = default_retry_timeout
        self._screenshot = None

    def _get_screenshot(self, force_full_page_screenshot):
        if force_full_page_screenshot:
            current_screenshot = self._driver.get_full_page_screenshot()
            return EyesScreenshot.create_from_image(current_screenshot, self._driver)
        current_screenshot64 = self._driver.get_screenshot_as_base64()
        return EyesScreenshot.create_from_base64(current_screenshot64, self._driver)

    @staticmethod
    def _create_match_data_bytes(app_output, user_inputs, tag, ignore_mismatch, screenshot):
        match_data = dict(appOutput=app_output, userInputs=user_inputs, tag=tag,
                          ignoreMismatch=ignore_mismatch)
        match_data_json_bytes = general_utils.to_json(match_data).encode('utf-8')
        match_data_size_bytes = pack(">L", len(match_data_json_bytes))
        screenshot_bytes = screenshot.get_bytes()
        body = match_data_size_bytes + match_data_json_bytes + screenshot_bytes
        return body

    def _prepare_match_data_for_window(self, tag, force_full_page_screenshot, user_inputs,
                                       ignore_mismatch=False):
        title = self._eyes.get_title()
        self._screenshot = self._get_screenshot(force_full_page_screenshot)
        app_output = {'title': title, 'screenshot64': None}
        return self._create_match_data_bytes(app_output, user_inputs, tag, ignore_mismatch,
                                             self._screenshot)

    def _prepare_match_data_for_region(self, region, tag, force_full_page_screenshot, user_inputs,
                                       ignore_mismatch=False):
        title = self._eyes.get_title()
        self._screenshot = self._get_screenshot(force_full_page_screenshot) \
            .get_sub_screenshot_by_region(region)
        app_output = {'title': title, 'screenshot64': None}
        return self._create_match_data_bytes(app_output, user_inputs, tag, ignore_mismatch,
                                             self._screenshot)

    def _prepare_match_data_for_element(self, element, tag, force_full_page_screenshot, user_inputs,
                                        ignore_mismatch=False):
        title = self._eyes.get_title()
        self._screenshot = self._get_screenshot(force_full_page_screenshot)
        self._screenshot = self._screenshot.get_sub_screenshot_by_element(element)
        app_output = {'title': title, 'screenshot64': None}
        return self._create_match_data_bytes(app_output, user_inputs, tag, ignore_mismatch,
                                             self._screenshot)

    def _run_with_intervals(self, prepare_action, retry_timeout):
        """
        Includes retries in case the screenshot does not match.
        """
        logger.debug('Matching with intervals...')
        # We intentionally take the first screenshot before starting the timer, to allow the page
        # just a tad more time to stabilize.
        data = prepare_action(ignore_mismatch=True)
        # Start the timer.
        start = time.time()
        logger.debug('First match attempt...')
        as_expected = self._agent_connector.match_window(self._running_session, data)
        if as_expected:
            return {"as_expected": True, "screenshot": self._screenshot}
        retry = time.time() - start
        logger.debug("Failed. Elapsed time: {0}".format(retry))
        while retry < retry_timeout:
            logger.debug('Matching...')
            time.sleep(self._MATCH_INTERVAL)
            data = prepare_action(ignore_mismatch=True)
            as_expected = self._agent_connector.match_window(self._running_session, data)
            if as_expected:
                return {"as_expected": True, "screenshot": self._screenshot}
            retry = time.time() - start
            logger.debug("Elapsed time: {0}".format(retry))
        # One last try
        logger.debug('One last matching attempt...')
        data = prepare_action()
        as_expected = self._agent_connector.match_window(self._running_session, data)
        return {"as_expected": as_expected, "screenshot": self._screenshot}

    def _run(self, prepare_action, run_once_after_wait=False, retry_timeout=-1):
        if retry_timeout < 0:
            retry_timeout = self._default_retry_timeout
        logger.debug("Matching timeout set to: {0}".format(retry_timeout))
        start = time.time()
        if run_once_after_wait or retry_timeout == 0:
            logger.debug("Matching once...")
            # If the load time is 0, the sleep would immediately return anyway.
            time.sleep(retry_timeout)
            data = prepare_action()
            as_expected = self._agent_connector.match_window(self._running_session, data)
            result = {"as_expected": as_expected, "screenshot": self._screenshot}
        else:
            result = self._run_with_intervals(prepare_action, retry_timeout)
        logger.debug("Match result: {0}".format(result["as_expected"]))
        elapsed_time = time.time() - start
        logger.debug("_run(): Completed in %.2f seconds" % elapsed_time)
        return result

    def match_window(self, retry_timeout, tag, force_full_page_screenshot, user_inputs,
                     run_once_after_wait=False):
        """
        Performs a match for a given region.
        """
        prepare_action = functools.partial(self._prepare_match_data_for_window, tag,
                                           force_full_page_screenshot, user_inputs)
        return self._run(prepare_action, run_once_after_wait, retry_timeout)

    def match_region(self, region, retry_timeout, tag, force_full_page_screenshot, user_inputs,
                     run_once_after_wait=False):
        """
        Performs a match for a given region.
        """
        prepare_action = functools.partial(self._prepare_match_data_for_region, region, tag,
                                           force_full_page_screenshot, user_inputs)
        return self._run(prepare_action, run_once_after_wait, retry_timeout)

    def match_element(self, element, retry_timeout, tag, force_full_page_screenshot, user_inputs,
                      run_once_after_wait=False):
        """
        Performs a match for a given element.
        """
        prepare_action = functools.partial(self._prepare_match_data_for_element, element,
                                           tag, force_full_page_screenshot, user_inputs)
        return self._run(prepare_action, run_once_after_wait, retry_timeout)