#coding:utf-8
from pyramid.config import Configurator
import pyramid_jinja2
import ztq_core
import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from ztq_console.utils import models
from ztq_console.utils.security import groupfinder


def main(global_config, redis_host='127.0.0.1', redis_port='6379', \
        redis_db='0', frs_root='frs', \
        frs_cache='frscache', addon_config=None, work_enable=True, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # 初始化Redis连接
    ztq_core.setup_redis('default', redis_host, port=int(redis_port), db=int(redis_db),)

    # # 开启后台服务
    # 初始化fts_web配置
    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    settings = dict(settings)
    settings.setdefault('jinja2.directories', 'ztq_console:templates')
    config = Configurator(settings=settings, root_factory='ztq_console.utils.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.begin()
    config.add_renderer('.html', pyramid_jinja2.renderer_factory)
    config.add_static_view('static', 'ztq_console:static')
    config.scan('ztq_console.views')  
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('password', '/password' )
    config.add_route('worker', '/worker/{id}', 
                    view='ztq_console.views.config_worker')
    config.add_route('end_thread', '/worker/{id}/{thread}/{pid}', 
                    view='ztq_console.views.stop_working_job') 
    config.add_route('taskqueue', '/taskqueues/{id}')
    config.add_route('taskqueues_config', '/taskqueues/{id}/config', 
                    view='ztq_console.views.config_queue')
    config.add_route('taskqueue_action', '/taskqueues_action/{id}')
    config.add_route('errorqueues_job', '/errorqueues/{id}/job',
                    view='ztq_console.views.error_jobs_handler')    
    config.add_route('workerlog', '/workerlog/{page}')
    config.add_route('syslog', '/syslog/{page}')
    config.add_route('errorlog', '/errorlog/{page}')
    config.add_route('errorqueue', '/errorqueue/{id}/{page}')
    config.add_route('redo_all_error_for_queue', '/redo_all_error_for_queue/{id}')
    config.add_route('del_all_error_for_queue', '/del_all_error_for_queue/{id}')
    if addon_config is not None:
        addon_config(config)
    config.end()

    return config.make_wsgi_app()

