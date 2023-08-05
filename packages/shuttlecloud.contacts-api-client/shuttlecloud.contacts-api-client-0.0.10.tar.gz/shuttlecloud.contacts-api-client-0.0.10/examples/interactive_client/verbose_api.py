import os
import sys
import time
import copy
import operator
import webbrowser

import console
import reflection

from shuttlecloud.contacts_api_client import ContactsApi


class ApiError(Exception):
    pass


def verbose_method(method):
    """
    Prints method arguments and return result.
    Decorates the specified method with such logic.
    """
    def format_pairs(pairs):
        def hide_password(value):
            try:
                result = copy.deepcopy(value)
                auth_struct = result["contactsextraction"]["sourceaccount"]["auth"]
                if "password" in auth_struct:
                    auth_struct["password"] = "*" * 4
            except (TypeError, AttributeError, KeyError):
                result = value
            return result
        return ["{} = {}".format(key, hide_password(value)) for (key, value) in pairs]

    def wrapper(*args, **kwargs):
        argument_names = reflection.get_argument_names(method)
        formatted_args = format_pairs(zip(argument_names, args))
        formatted_kwargs = format_pairs(kwargs.items())
        formatted_input = "\n".join(formatted_args + formatted_kwargs)

        print "\nAPI call arguments:\n{}".format(formatted_input)

        print "\nProcessing...",
        sys.stdout.flush()
        start_time = time.time()
        result = method(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print "done (in {:.2f} s)".format(elapsed_time)

        status, data = result
        formatted_data = str(data)
        visible_characters = 512
        skipped_characters = max(0, len(formatted_data) - visible_characters)
        formatted_status = "status = {}".format(status)
        formatted_data = "data = {}".format(formatted_data[:visible_characters])
        formatted_output = "\n".join((formatted_status, formatted_data))
        print "\nAPI call result:\n{}".format(formatted_output)
        if skipped_characters:
            print "Skipped {} bytes".format(skipped_characters)
        print "\n", "-" * 80
        return result
    return wrapper


class VerboseContactsApi(ContactsApi):

    def __init__(self, api_url, app_id, secret_token, oauth_handlers=None):
        ContactsApi.__init__(self, api_url, app_id, secret_token)
        # wrap request method with pretty-printing decorator
        self._api_client.request = verbose_method(self._api_client.request)
        self._oauth_handlers = oauth_handlers or dict()
        self._console = console.Console()

    def _get_token_auth(self, provider):
        try:
            handler = self._oauth_handlers[provider]
        except KeyError:
            raise ApiError("OAuth not implemented for provider '{}'".format(provider))

        print "Complete the OAuth process and extract your access token from the address bar"
        url = handler.get_url()
        webbrowser.open(url)

        token = self._console.explicit_input("access token")
        auth = handler.get_auth(token)
        return auth

    def _get_password_auth(self, provider):
        password = self._console.password_input("password", repeat=True)
        auth = {
            "password": password,
        }
        return auth

    def load(self, email):
        """
        Loads a job for extracting contacts from the given email account.
        """
        provider, auth_type = self._verify_capabilities(email)

        try:
            auth_factory = {
                self.BASIC_AUTHENTICATION: self._get_password_auth,
                self.OAUTH_AUTHENTICATION: self._get_token_auth,
            }[auth_type]
        except KeyError:
            raise ApiError("Unsupported authentication method: '{}'".format(auth_type))

        auth = auth_factory(provider)
        response = ContactsApi.load(self, email, auth)
        return response

    def flow(self, email):
        """
        Executes the entire flow: capabilities, load, status, contacts,
        and saves the addressbook to a file.
        """
        job_id = self._load_job(email)
        operation_id = self._check_status(job_id)
        vcards = self._fetch_contacts(operation_id)
        filename = "addressbook-{}.vcf".format(email)
        self._save_addressbook(vcards, filename)
        print "\nContacts extracted: {}\nSaved to file: '{}'".format(len(vcards), filename)

    def _assert_success(self, status_code):
        if not str(status_code).startswith("2"):
            raise ApiError("Request failed with status {}".format(status_code))

    def _verify_capabilities(self, email):
        status_code, data = self.capabilities(email)
        self._assert_success(status_code)
        provider = data["provider"]

        try:
            auth_type = data["contactsextraction"][0]["type"]
        except (KeyError, IndexError):
            raise ApiError("Provider '{}' not supported".format(provider))

        print "Provider '{}' supported with '{}' authentication method".format(provider, auth_type)
        return provider, auth_type

    def _load_job(self, email):
        status_code, data = self.load(email)
        self._assert_success(status_code)

        if data.get("status", "error") != "success":
            raise ApiError("Loading job failed")

        job_id = data["jobid"]
        return job_id

    def _check_status(self, job_id):
        status_code, data = self.status(job_id)
        self._assert_success(status_code)
        operation_id = data.keys()[0]
        return operation_id

    def _fetch_contacts(self, operation_id):
        status = self.JOB_STARTED
        all_vcards = list()

        while status != self.JOB_COMPLETED:
            time.sleep(3)
            status_code, data = self.contacts(operation_id)
            self._assert_success(status_code)
            status = data["status"]

            if status == self.JOB_PENDING:
                raise ApiError("Invalid password")

            if status == self.JOB_REVIEW:
                raise ApiError("Extraction process failed")

            if "contacts" in data:
                vcards = map(operator.itemgetter("vcard"), data["contacts"])
                all_vcards.extend(vcards)
        return all_vcards

    def _save_addressbook(self, vcards, filename):
        encoded_vcards = [vcard.encode("utf-8") for vcard in vcards]

        with open(filename, "w") as handle:
            handle.write(os.linesep.join(encoded_vcards))
