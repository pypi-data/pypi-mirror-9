# vCloud Air CLI 0.1
# 
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the Apache License, Version 2.0 (the "License").  
# You may not use this product except in compliance with the License.  
#
# This product may include a number of subcomponents with
# separate copyright notices and license terms. Your use of the source
# code for the these subcomponents is subject to the terms and
# conditions of the subcomponent's license, as noted in the LICENSE file. 
#

# coding: utf-8

import sys
import operator
import click
import time
import random
import ConfigParser
import os
import yaml
import pkg_resources
import ConfigParser
import logging
import httplib
import json
from os.path import expanduser
from tabulate import tabulate
from time import sleep

from pyvcloud.vcloudair import VCA
# from pyvcloud.vclouddirector import VCD
# from pyvcloud.vapp import VAPP
# from pyvcloud.helper import generalHelperFunctions as ghf

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('-p', '--profile', default='', metavar='<profile>', help='Profile id')
@click.option('-v', '--version', is_flag=True, help='Show version')
@click.option('-d', '--debug', is_flag=True, help='Enable debug')
@click.option('-j', '--json', 'json_output', is_flag=True, help='Results as JSON object')
@click.option('-i', '--insecure', is_flag=True, help='Perform insecure SSL connections')
@click.pass_context
def cli(ctx, profile, version, debug, json_output, insecure):
    """VMware vCloud Air Command Line Interface."""
    config = ConfigParser.RawConfigParser()
    config.read(os.path.expanduser('~/.vcarc'))    
    ctx.obj={}
    if profile != '':
        ctx.obj['PROFILE'] = profile
    else:
        section = 'Global'
        if config.has_option(section, 'profile'):
            ctx.obj['PROFILE'] = config.get(section, 'profile')
        else:
            ctx.obj['PROFILE'] = 'default'    
   
    section = 'Profile-%s' % ctx.obj['PROFILE']
    if config.has_option(section, "host"):
        ctx.obj['host'] = config.get(section, "host")
    else:
        ctx.obj['host'] = ''
    if config.has_option(section, "user"):
        ctx.obj['user'] = config.get(section, "user")
    else:
        ctx.obj['user'] = ''        
    if config.has_option(section, "token"):
        ctx.obj['token'] = config.get(section, "token")
    else:
        ctx.obj['token'] = ''        
    if config.has_option(section, "token_vcd"):
        ctx.obj['token_vcd'] = config.get(section, "token_vcd")        
    else:
        ctx.obj['token_vcd'] = ''
    if config.has_option(section, "service_type"):
        ctx.obj['service_type'] = config.get(section, "service_type")
    else:
        ctx.obj['service_type'] = ''
    if config.has_option(section, "service_version"):
        ctx.obj['service_version'] = config.get(section, "service_version")
    else:
        ctx.obj['service_version'] = ''
    if config.has_option(section, "service"):
        ctx.obj['service'] = config.get(section, "service")
    else:
        ctx.obj['service'] = ''
    if config.has_option(section, "datacenter"):
        ctx.obj['datacenter'] = config.get(section, "datacenter")
    else:
        ctx.obj['datacenter'] = ''
    if config.has_option(section, "instance"):
        ctx.obj['instance'] = config.get(section, "instance")
    else:
        ctx.obj['instance'] = ''
    if config.has_option(section, "api_url"):
        ctx.obj['api_url'] = config.get(section, "api_url")
    else:
        ctx.obj['api_url'] = ''
    if config.has_option(section, "org"):
        ctx.obj['org'] = config.get(section, "org")
    else:
        ctx.obj['org'] = ''
        
    ctx.obj['verify'] = not insecure

    ctx.obj['json_output'] = json_output

    if debug:
        httplib.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
    if version:
        version = pkg_resources.require("vca-cli")[0].version
        version_pyvcloud = pkg_resources.require("pyvcloud")[0].version
        print_message('vca-cli version %s (pyvcloud: %s)' % (version, version_pyvcloud), ctx.obj['json_output'])
    else:
        if ctx.invoked_subcommand is None:
               help_text = ctx.get_help()
               print help_text        
    
#todo: add --list-vdcs / orgs    
@cli.command()
@click.pass_context
@click.argument('user')
@click.option('-t', '--type', 'service_type', default='ondemand', metavar='[subscription | ondemand | vcd ]', type=click.Choice(['subscription', 'ondemand', 'vcd']), help='')
@click.option('-v', '--version', 'service_version', default='5.7', metavar='[5.5 | 5.6 | 5.7]', type=click.Choice(['5.5', '5.6', '5.7']), help='')
@click.option('-H', '--host', default='https://iam.vchs.vmware.com', help='')
@click.option('-p', '--password', prompt=True, confirmation_prompt=False, hide_input=True, help='Password')
@click.option('-i', '--instance', default=None, help='Instance Id')
def login(ctx, user, host, password, service_type, service_version, instance):
    """Login to a vCloud service"""
    if not (host.startswith('https://') or host.startswith('http://')):
        host = 'https://' + host              
    vca = VCA()
    result = vca.login(host, user, password, None, None, service_type, service_version, ctx.obj['verify'])
    if result:
        if (instance):
            result = vca.login_to_instance(password, instance, ctx.obj['verify'])
        
        print_message('Login successful for profile \'%s\'' % ctx.obj['PROFILE'], ctx.obj['json_output'])
        config = ConfigParser.RawConfigParser()
        config.read(os.path.expanduser('~/.vcarc'))
        section = 'Profile-%s' % ctx.obj['PROFILE']
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, 'host', host)
        config.set(section, 'user', user)
        config.set(section, 'token', vca.token)
        config.set(section, 'token_vcd', vca.token_vcd)        
        config.set(section, 'service_type', service_type)
        config.set(section, 'service_version', service_version)
        config.set(section, 'instance', instance)
        config.set(section, 'org', vca.org)
        config.set(section, 'api_url', vca.api_url)
        with open(os.path.expanduser('~/.vcarc'), 'w+') as configfile:
            config.write(configfile)
    else:
        print_error('login failed', ctx.obj['json_output'])
    return result
    
@cli.command()
@click.pass_context
def logout(ctx):
    """Logout from a vCloud service"""
    vca = _getVCA(ctx)
    vca.logout(ctx.obj['verify'])
    config = ConfigParser.RawConfigParser()
    config.read(os.path.expanduser('~/.vcarc'))
    section = 'Profile-%s' % ctx.obj['PROFILE']
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, 'token', 'None')
    config.set(section, 'token_vcd', 'None')        
    with open(os.path.expanduser('~/.vcarc'), 'w+') as configfile:
        config.write(configfile)
    print_message('Logout successful for profile \'%s\'' % ctx.obj['PROFILE'], ctx.obj['json_output'])        
    
#todo: tabulate output    
@cli.command()
@click.pass_context
def status(ctx):
    """Show current status"""   
    vca = _getVCA(ctx)
    if (ctx.obj['json_output']):
        json_msg = {"profile": ctx.obj['PROFILE'],
                    "host": ctx.obj['host'],
                    "service_type": ctx.obj['service_type'],
                    "service_version": ctx.obj['service_version'],
                    "user": ctx.obj['user'],
                    "session": 'active' if vca else'inactive'
                    }
        print json.dumps(json_msg, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        click.secho("profile:         %s" % ctx.obj['PROFILE'] , fg='blue')
        click.secho("host:            %s" % ctx.obj['host'], fg='blue')
        click.secho("service type:    %s" % ctx.obj['service_type'], fg='blue')   
        click.secho("service version: %s" % ctx.obj['service_version'], fg='blue')         
        click.secho("user:            %s" % ctx.obj['user'], fg='blue')
        if vca != None:
            click.secho("session:         %s" % 'active', fg='blue') 
        else:
            click.secho("session:         %s" % 'inactive', fg='red') 

    # click.secho("service:         %s" % ctx.obj['service'], fg='blue')
    # click.secho("datacenter:      %s" % ctx.obj['datacenter'], fg='blue')
    # click.secho("gateway:         %s" % ctx.obj['gateway'], fg='blue')
    # click.secho("instance:        %s" % ctx.obj['instance'], fg='blue')    
    
@cli.command()
@click.pass_context
@click.argument('operation', default='list', metavar='[list | details]', type=click.Choice(['list', 'details']))
@click.option('-o', '--org', default='', metavar='<org>', help='Org Name')
def orgs(ctx, operation, org):
    """Operations with Organizations"""
    vca = _getVCA(ctx)
    if not vca:
        print_error('User not authenticated or token expired', ctx.obj['json_output'])
        return
    if 'list' == operation:
        headers = ["Name", "href"]
        orgs = vca.get_orgs(ctx.obj['verify'])
        org_list = orgs.get_Org() if orgs else []
        table = [[org.get_name(), org.get_href()] for org in org_list]
        print_table("Available orgs for user '%s' in '%s' profile:" % (ctx.obj['user'], ctx.obj['PROFILE']), 'orgs', headers, table, ctx.obj['json_output'])
    elif 'details' == operation:
        headers = ["Type", "Name"]
        org_details = vca.get_org(org, ctx.obj['verify'])
        links = org_details.Link if org_details else []        
        table = [[details.get_type().split('.')[-1].split('+')[0], details.get_name()] for details in filter(lambda info: info.name, links)]
        sorted_table = sorted(table, key=operator.itemgetter(1), reverse=True)        
        print_table("Details for org '%s':" % (org), 'orgs', headers, sorted_table, ctx.obj['json_output'])        
        
@cli.command()
@click.pass_context
@click.argument('operation', default='list', metavar='[list | details]', type=click.Choice(['list', 'details']))
@click.option('-i', '--instance', default='', metavar='<instance>', help='Instance Id')
def instances(ctx, operation, instance):
    """Operations with Instances"""
    vca = _getVCA(ctx)
    if not vca:
        print_error('User not authenticated or token expired', ctx.obj['json_output'])
        return
    if 'list' == operation:
        headers = ["Instance Id", "Description", "Region", "Plan Id"]
        instances = vca.get_instances(ctx.obj['verify'])        
        items = instances if instances else []
        table = [[item['id'], item['description'], item['region'], item['planId']] for item in items]
        print_table("Available instances for user '%s' in '%s' profile:" % (ctx.obj['user'], ctx.obj['PROFILE']), 'orgs', headers, table, ctx.obj['json_output'])
        
    elif 'details' == operation:
        pass
        
def _getVCA(ctx):
    vca = VCA()
    if vca.re_login(ctx.obj['api_url'], ctx.obj['token_vcd'], ctx.obj['service_version'], ctx.obj['verify']):
        return vca
    if vca.login(ctx.obj['host'], ctx.obj['user'], None, ctx.obj['token'], ctx.obj['token_vcd'], ctx.obj['service_type'], ctx.obj['service_version'], ctx.obj['verify']):
        return vca
    else:
        return None
        
def print_table(msg, obj, headers, table, json_output):    
    if json_output:
        data = [dict(zip(headers, row)) for row in table]
        print json.dumps({"Errorcode" : "0" , "Details" : msg, obj : data}, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        click.echo(click.style(msg, fg='blue'))
        print tabulate(table, headers = headers, tablefmt="orgtbl")
        
def print_message(msg, json_output):
    if json_output:
        json_msg = {"Returncode" : "1", "Details" : msg}        
        print json.dumps(json_msg, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        click.secho(msg, fg='blue')
    
def print_error(msg, json_output):    
    if json_output:
        json_msg = {"Errorcode" : "1", "Details" : msg}
        print json.dumps(json_msg, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        click.secho(msg, fg='red')

if __name__ == '__main__':
    cli(obj={})
