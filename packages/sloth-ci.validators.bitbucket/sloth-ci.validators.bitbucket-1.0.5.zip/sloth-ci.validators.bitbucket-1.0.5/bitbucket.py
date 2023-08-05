'''Bitbucket Sloth CI validator that validates the `Bitbucket <https://bitbucket.org/>`_ payload against username and repo name (obtained from the Sloth app config).'''


__title__ = 'sloth-ci.validators.bitbucket'
__description__ = 'Bitbucket validator for Sloth CI'
__version__ = '1.0.5'
__author__ = 'Konstantin Molchanov'
__author_email__ = 'moigagoo@live.com'
__license__ = 'MIT'


def validate(request, validation_data):
    '''Validate Bitbucket payload against repo name (obtained from the Sloth app config).

    :param request_params: payload to validate
    :param validation_data: dictionary with the key ``repo`` (in the form "username/repo")

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

        repo = '{owner}/{slug}'.format(
            owner=parsed_payload['repository']['owner'],
            slug=parsed_payload['repository']['slug']
        )

        if repo != validation_data['repo']:
            return (403, 'Payload validation failed: repo mismatch. Repo: %s' % repo, [])

        branches = {commit['branch'] for commit in parsed_payload['commits']}

        param_dicts = [{'branch': branch} for branch in branches]

        return (200, 'Payload validated. Branches: %s' % ', '.join(branches), param_dicts)

    except Exception as e:
        return (400, 'Payload validation failed: %s' % e, [])
