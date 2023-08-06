'''Bitbucket Sloth CI validator that validates the `Bitbucket <https://bitbucket.org/>`_ payload against username and repo name (obtained from the Sloth app config).

Usage in the app config::

    provider:
        bitbucket:
            # Repository owner. Mandatory parameter.
            owner: moigagoo

            # Repository title as it appears in the URL, i.e. slug.
            # Mandatory parameter.
            repo: sloth-ci

            # Only pushes to these branches will initiate a build.
            # Skip this parameter to allow all branches to fire builds.
            branches:
                - master
                - staging
'''


__title__ = 'sloth-ci.validators.bitbucket'
__description__ = 'Bitbucket validator for Sloth CI'
__version__ = '1.0.6'
__author__ = 'Konstantin Molchanov'
__author_email__ = 'moigagoo@live.com'
__license__ = 'MIT'


def validate(request, validation_data):
    '''Validate Bitbucket payload against repo name (obtained from the Sloth app config).

    :param request_params: payload to validate
    :param validation_data: dictionary with the keys ``owner``, ``repo``, and ``branches``

    :returns: (status, message, list of extracted param dicts)
    '''

    from json import loads

    if request.method != 'POST':
        return (405, 'Payload validation failed: Wrong method, POST expected, got %s.' % request.method, [])

    trusted_ips = ['131.103.20.165', '131.103.20.166']

    remote_ip = request.remote.ip

    if remote_ip not in trusted_ips:
        return (403, 'Payload validation failed: Unverified remote IP: %s.' % remote_ip, [])

    try:
        payload = request.params.get('payload')

        parsed_payload = loads(payload)

        owner = parsed_payload['repository']['owner']

        if owner != validation_data['owner']:
            return (403, 'Payload validation failed: wrong owner: %s' % owner, [])

        repo = parsed_payload['repository']['slug']

        if repo != validation_data['repo']:
            return (403, 'Payload validation failed: wrong repository: %s' % repo, [])

        branches = {commit['branch'] for commit in parsed_payload['commits']}

        allowed_branches = set(validation_data.get('branches', branches))

        if not branches & allowed_branches:
            return (403, 'Payload validation failed: wrong branches: %s' % branches, [])

        param_dicts = [{'branch': branch} for branch in branches & allowed_branches]

        return (200, 'Payload validated. Branches: %s' % ', '.join(branches), param_dicts)

    except Exception as e:
        return (400, 'Payload validation failed: %s' % e, [])
