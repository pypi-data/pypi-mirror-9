Interactive API Example
=======================

API Credentials
--------------
    - Go to [the official API sign up site](https://shuttlecloud.com/account) to create a developer account
      and obtain an access token/secret. Updated settings.py file.

Usage
-----
    contacts_api --flow email
    contacts_api (--capabilities email | --contacts operation_id |
                          --load email | --status job_id | --interactive)


      --flow email              Executes the entire flow to extract contacts and saves
                                    the addressbook to a file.

      The following options correspond to specific API methods:

      --capabilities email      Verifies whether the email address is supported.
      --contacts operation_id   Fetches a chunk of vcards for the given operation_id.
      --load email              Loads a job for extracting contacts from the given
                                    email account.
      --status job_id           Checks the status for the given job_id.

      --interactive             Select methods and arguments interactively.
      -h, --help                show this help message and exit.

Comments
--------
    - 'flow' mode exercises all of the API methods in a form of a typical use case,
        i.e. for the given email, contacts are extracted and saved to a vcard file.
    - 'capabilities', 'load', 'status' and 'contacts' modes correspond
        to identically named API methods.
    - 'interactive' mode allows to select the API method and provide arguments
        step by step.

Examples
--------
    - Extract all the contacts from a given account.
        python shuttlecloud_api.py --flow username@provider.com

    - Check support for the email provider.
        python shuttlecloud_api.py --capabilities username@provider.com

    - Load a contacts extraction job.
        python shuttlecloud_api.py --load username@provider.com

    - Check status of the job.
        python shuttlecloud_api.py --status 12982a3dbcfe4c289d4207c9d3b99f18

    - Fetch contacts batch.
        python shuttlecloud_api.py --contacts a1edfad994344c719be194ef9177aa5f

    - Enter to interactive mode.
        python shuttlecloud_api.py --interactive
