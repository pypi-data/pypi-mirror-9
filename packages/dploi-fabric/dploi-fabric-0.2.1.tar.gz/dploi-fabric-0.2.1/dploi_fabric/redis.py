# -*- coding: utf-8 -*-

import StringIO
import posixpath
from fabric.decorators import task
from fabric.api import run, env, put

from dploi_fabric.toolbox.template import render_template
from dploi_fabric.utils import config


@task
def update_config_file(dryrun=False):
    for site, site_config in config.sites.items():
        redis_processes = [(x, site_config.processes[x]) for x in site_config.processes if site_config.processes[x]["type"] == "redis"]
        template_path = site_config['redis']['template']
        print redis_processes
        for process_name, process in redis_processes:
            working_directoy = posixpath.normpath(posixpath.join(env.path, '..', 'data', 'redis', process_name))
            log_directory = posixpath.normpath(posixpath.join(site_config['deployment']['logdir'], 'log', 'redis'))
            run('mkdir -p ' + working_directoy)
            run('mkdir -p ' + log_directory)
            context_dict = site_config
            context_dict.update({
                'site': site,
                'working_directory': working_directoy,
                'log_directory': log_directory,
                'process_name': process_name,
                'socket': process['socket'],
            })
            path = posixpath.abspath(posixpath.join(site_config['deployment']['path'], '..', 'config', process_name + '.conf'))
            output = render_template(template_path, context_dict)
            if dryrun:
                print path + ":"
                print output
            else:
                put(StringIO.StringIO(output), path)

