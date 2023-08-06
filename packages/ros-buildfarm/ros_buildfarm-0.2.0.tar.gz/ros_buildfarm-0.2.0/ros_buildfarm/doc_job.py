from __future__ import print_function

import sys

from catkin_pkg.package import parse_package_string
from rosdistro import get_distribution_cache
from rosdistro import get_index

from ros_buildfarm.common import get_doc_job_name
from ros_buildfarm.common import get_doc_view_name
from ros_buildfarm.common import git_github_orgunit
from ros_buildfarm.common import get_github_project_url
from ros_buildfarm.common \
    import get_repositories_and_script_generating_key_files
from ros_buildfarm.common import JobValidationError
from ros_buildfarm.config import get_distribution_file
from ros_buildfarm.config import get_doc_build_files
from ros_buildfarm.config import get_global_doc_build_files
from ros_buildfarm.config import get_index as get_config_index
from ros_buildfarm.git import get_repository
from ros_buildfarm.templates import expand_template


def configure_doc_jobs(
        config_url, rosdistro_name, doc_build_name, groovy_script=None):
    """
    Configure all Jenkins doc jobs.

    L{configure_doc_job} will be invoked for doc repository and target
    which matches the build file criteria.
    """
    config = get_config_index(config_url)
    build_files = get_doc_build_files(config, rosdistro_name)
    build_file = build_files[doc_build_name]

    index = get_index(config.rosdistro_index_url)

    dist_cache = None
    if build_file.notify_maintainers:
        dist_cache = get_distribution_cache(index, rosdistro_name)

    # get targets
    targets = []
    for os_name in build_file.targets.keys():
        for os_code_name in build_file.targets[os_name].keys():
            for arch in build_file.targets[os_name][os_code_name]:
                targets.append((os_name, os_code_name, arch))
    print('The build file contains the following targets:')
    for os_name, os_code_name, arch in targets:
        print('  -', os_name, os_code_name, arch)

    dist_file = get_distribution_file(index, rosdistro_name, build_file)
    if not dist_file:
        print('No distribution file matches the build file')
        return

    doc_view_name = get_doc_view_name(rosdistro_name, doc_build_name)

    from ros_buildfarm.jenkins import connect
    jenkins = connect(config.jenkins_url)

    views = []
    views.append(configure_doc_view(jenkins, doc_view_name))

    if groovy_script is not None:
        # all further configuration will be handled by the groovy script
        jenkins = False

    repo_names = dist_file.repositories.keys()
    filtered_repo_names = build_file.filter_repositories(repo_names)

    job_names = []
    job_configs = {}
    for repo_name in sorted(repo_names):
        is_disabled = repo_name not in filtered_repo_names
        if is_disabled and build_file.skip_ignored_repositories:
            print("Skipping ignored repository '%s'" % repo_name,
                  file=sys.stderr)
            continue

        repo = dist_file.repositories[repo_name]
        if not repo.doc_repository:
            print("Skipping repository '%s': no doc section" % repo_name)
            continue
        if not repo.doc_repository.version:
            print("Skipping repository '%s': no doc version" % repo_name)
            continue

        for os_name, os_code_name, arch in targets:
            try:
                job_name, job_config = configure_doc_job(
                    config_url, rosdistro_name, doc_build_name,
                    repo_name, os_name, os_code_name, arch,
                    config=config, build_file=build_file,
                    index=index, dist_file=dist_file,
                    dist_cache=dist_cache, jenkins=jenkins, views=views,
                    is_disabled=is_disabled,
                    groovy_script=groovy_script)
                job_names.append(job_name)
                if groovy_script is not None:
                    print("Configuration for job '%s'" % job_name)
                    job_configs[job_name] = job_config
            except JobValidationError as e:
                print(e.message, file=sys.stderr)

    job_prefix = '%s__' % doc_view_name
    if groovy_script is None:
        # delete obsolete jobs in this view
        from ros_buildfarm.jenkins import remove_jobs
        print('Removing obsolete doc jobs')
        remove_jobs(jenkins, job_prefix, job_names)
    else:
        print("Writing groovy script '%s' to reconfigure %d jobs" %
              (groovy_script, len(job_configs)))
        data = {
            'job_configs': job_configs,
            'job_prefixes_and_names': {
                'doc': (job_prefix, job_names),
            }
        }
        content = expand_template('snippet/reconfigure_jobs.groovy.em', data)
        with open(groovy_script, 'w') as h:
            h.write(content)


def configure_doc_job(
        config_url, rosdistro_name, doc_build_name,
        repo_name, os_name, os_code_name, arch,
        config=None, build_file=None,
        index=None, dist_file=None, dist_cache=None,
        jenkins=None, views=None,
        is_disabled=False,
        groovy_script=None,
        doc_repository=None):
    """
    Configure a single Jenkins doc job.

    This includes the following steps:
    - clone the doc repository to use
    - clone the ros_buildfarm repository
    - write the distribution repository keys into files
    - invoke the run_doc_job.py script
    """
    if config is None:
        config = get_config_index(config_url)
    if build_file is None:
        build_files = get_doc_build_files(config, rosdistro_name)
        build_file = build_files[doc_build_name]

    if index is None:
        index = get_index(config.rosdistro_index_url)
    if dist_file is None:
        dist_file = get_distribution_file(index, rosdistro_name, build_file)
        if not dist_file:
            raise JobValidationError(
                'No distribution file matches the build file')

    repo_names = dist_file.repositories.keys()

    if repo_name is not None:
        if repo_name not in repo_names:
            raise JobValidationError(
                "Invalid repository name '%s' " % repo_name +
                'choose one of the following: %s' %
                ', '.join(sorted(repo_names)))

        repo = dist_file.repositories[repo_name]
        if not repo.doc_repository:
            raise JobValidationError(
                "Repository '%s' has no doc section" % repo_name)
        if not repo.doc_repository.version:
            raise JobValidationError(
                "Repository '%s' has no doc version" % repo_name)
        doc_repository = repo.doc_repository

    if os_name not in build_file.targets.keys():
        raise JobValidationError(
            "Invalid OS name '%s' " % os_name +
            'choose one of the following: ' +
            ', '.join(sorted(build_file.targets.keys())))
    if os_code_name not in build_file.targets[os_name].keys():
        raise JobValidationError(
            "Invalid OS code name '%s' " % os_code_name +
            'choose one of the following: ' +
            ', '.join(sorted(build_file.targets[os_name].keys())))
    if arch not in build_file.targets[os_name][os_code_name]:
        raise JobValidationError(
            "Invalid architecture '%s' " % arch +
            'choose one of the following: %s' % ', '.join(sorted(
                build_file.targets[os_name][os_code_name])))

    if dist_cache is None and build_file.notify_maintainers:
        dist_cache = get_distribution_cache(index, rosdistro_name)
    if jenkins is None:
        from ros_buildfarm.jenkins import connect
        jenkins = connect(config.jenkins_url)
    if views is None:
        view_name = get_doc_view_name(
            rosdistro_name, doc_build_name)
        configure_doc_view(jenkins, view_name)

    job_name = get_doc_job_name(
        rosdistro_name, doc_build_name,
        repo_name, os_name, os_code_name, arch)

    job_config = _get_doc_job_config(
        config, config_url, rosdistro_name, doc_build_name,
        build_file, os_name, os_code_name, arch, doc_repository,
        repo_name, dist_cache=dist_cache, is_disabled=is_disabled)
    # jenkinsapi.jenkins.Jenkins evaluates to false if job count is zero
    if isinstance(jenkins, object) and jenkins is not False:
        from ros_buildfarm.jenkins import configure_job
        configure_job(jenkins, job_name, job_config)

    return job_name, job_config


def configure_doc_view(jenkins, view_name):
    from ros_buildfarm.jenkins import configure_view
    return configure_view(
        jenkins, view_name, include_regex='%s__.+' % view_name,
        template_name='dashboard_view_all_jobs.xml.em')


def _get_doc_job_config(
        config, config_url, rosdistro_name, doc_build_name,
        build_file, os_name, os_code_name, arch, doc_repo_spec,
        repo_name, dist_cache=None, is_disabled=False):
    template_name = 'doc/doc_job.xml.em'

    repository_args, script_generating_key_files = \
        get_repositories_and_script_generating_key_files(build_file=build_file)

    maintainer_emails = set([])
    if build_file.notify_maintainers and dist_cache and repo_name:
        # add maintainers listed in latest release to recipients
        repo = dist_cache.distribution_file.repositories[repo_name]
        if repo.release_repository:
            for pkg_name in repo.release_repository.package_names:
                if pkg_name not in dist_cache.release_package_xmls:
                    continue
                pkg_xml = dist_cache.release_package_xmls[pkg_name]
                pkg = parse_package_string(pkg_xml)
                for m in pkg.maintainers:
                    maintainer_emails.add(m.email)

    job_data = {
        'github_url': get_github_project_url(doc_repo_spec.url),

        'job_priority': build_file.jenkins_job_priority,
        'node_label': build_file.jenkins_job_label,

        'doc_repo_spec': doc_repo_spec,

        'disabled': is_disabled,

        'github_orgunit': git_github_orgunit(doc_repo_spec.url),

        'ros_buildfarm_repository': get_repository(),

        'script_generating_key_files': script_generating_key_files,

        'config_url': config_url,
        'rosdistro_index_url': config.rosdistro_index_url,
        'rosdistro_name': rosdistro_name,
        'doc_build_name': doc_build_name,
        'os_name': os_name,
        'os_code_name': os_code_name,
        'arch': arch,
        'repository_args': repository_args,

        'notify_emails': build_file.notify_emails,
        'maintainer_emails': maintainer_emails,
        'notify_maintainers': build_file.notify_maintainers,
        'notify_committers': build_file.notify_committers,

        'timeout_minutes': build_file.jenkins_job_timeout,

        'credential_id': build_file.upload_credential_id,
    }
    job_config = expand_template(template_name, job_data)
    return job_config


def configure_doc_metadata_job(
        config_url, rosdistro_name, doc_build_name,
        config=None, build_file=None):
    if config is None:
        config = get_config_index(config_url)
    if build_file is None:
        build_files = get_doc_build_files(config, rosdistro_name)
        build_file = build_files[doc_build_name]

    from ros_buildfarm.jenkins import connect
    jenkins = connect(config.jenkins_url)

    job_name = get_doc_view_name(rosdistro_name, doc_build_name)

    job_config = _get_doc_metadata_job_config(
        config, config_url, rosdistro_name, doc_build_name, build_file)
    # jenkinsapi.jenkins.Jenkins evaluates to false if job count is zero
    if isinstance(jenkins, object) and jenkins is not False:
        from ros_buildfarm.jenkins import configure_job
        configure_job(jenkins, job_name, job_config)


def _get_doc_metadata_job_config(
        config, config_url, rosdistro_name, doc_build_name, build_file):
    template_name = 'doc/doc_metadata_job.xml.em'

    repository_args, script_generating_key_files = \
        get_repositories_and_script_generating_key_files(config=config)

    job_data = {
        'job_priority': build_file.jenkins_job_priority,
        'node_label': build_file.jenkins_job_label,

        'ros_buildfarm_repository': get_repository(),

        'script_generating_key_files': script_generating_key_files,

        'config_url': config_url,
        'rosdistro_name': rosdistro_name,
        'doc_build_name': doc_build_name,
        'repository_args': repository_args,

        'notify_emails': build_file.notify_emails,

        'timeout_minutes': build_file.jenkins_job_timeout,

        'credential_id': build_file.upload_credential_id,
    }
    job_config = expand_template(template_name, job_data)
    return job_config


def configure_doc_independent_job(
        config_url, doc_build_name, config=None, build_file=None):
    if config is None:
        config = get_config_index(config_url)
    if build_file is None:
        build_files = get_global_doc_build_files(config)
        build_file = build_files[doc_build_name]

    from ros_buildfarm.jenkins import connect
    jenkins = connect(config.jenkins_url)

    job_name = 'doc_%s' % doc_build_name

    job_config = _get_doc_independent_job_config(
        config, config_url, job_name, build_file)
    # jenkinsapi.jenkins.Jenkins evaluates to false if job count is zero
    if isinstance(jenkins, object) and jenkins is not False:
        from ros_buildfarm.jenkins import configure_job
        configure_job(jenkins, job_name, job_config)


def _get_doc_independent_job_config(
        config, config_url, doc_build_name, build_file):
    template_name = 'doc/doc_independent_job.xml.em'

    repository_args, script_generating_key_files = \
        get_repositories_and_script_generating_key_files(config=config)

    job_data = {
        'job_priority': build_file.jenkins_job_priority,
        'node_label': build_file.jenkins_job_label,

        'ros_buildfarm_repository': get_repository(),

        'doc_repositories': build_file.doc_repositories,

        'script_generating_key_files': script_generating_key_files,

        'config_url': config_url,
        'doc_build_name': doc_build_name,
        'repository_args': repository_args,

        'notify_emails': build_file.notify_emails,

        'timeout_minutes': build_file.jenkins_job_timeout,

        'credential_id': build_file.upload_credential_id,
    }
    job_config = expand_template(template_name, job_data)
    return job_config
