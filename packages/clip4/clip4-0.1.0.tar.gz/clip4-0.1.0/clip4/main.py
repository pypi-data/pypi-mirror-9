#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from dropbox.client import DropboxOAuth2FlowNoRedirect, DropboxClient
from dropbox import rest as dbrest
from dropbox.datastore import DatastoreManager, Datastore, Date

import os
import sys
import argparse
import configparser
import webbrowser
import datetime

# YMK Get an OAuth2 user 19603889 token HBfujyMbh6MAAAAAAAACAB-1qIulPmBdQHqasXeGN5CTVId6by4cLCYpKlOkA4xu

program_name = 'clip4'


class command():
    """ base clip4 command class """

    def __init__(self, client):
        self.client = client

    @staticmethod
    def add_sub_command(sub_par):
        pass

    def __call__(self, args=None):
        if args is not None:
            self.args = args
            self.do_command()

    def do_command(self):
        pass


class command_get(command):
    " clip4 command 'get' """

    @staticmethod
    def add_sub_command(sub_par):
        cmdparser = sub_par.add_parser('get')
        cmdparser.add_argument('-s', '--session', default='global')
        cmdparser.add_argument('-i', '--index', type=int, default=0)

    def do_command(self):
        manager = DatastoreManager(self.client)
        clip4_datastore = manager.open_or_create_datastore(program_name)
        clip4_table = clip4_datastore.get_table(self.args.session)
        # print("YMK get args {0}".format(self.args))
        buffers = list(clip4_table.query(index=self.args.index))
        if len(buffers) != 0:
            print(buffers[0].get('buffer'))


class command_list(command):
    " clip4 command 'list' """

    @staticmethod
    def add_sub_command(sub_par):
        cmdparser = sub_par.add_parser('list')
        cmdparser.add_argument('-s', '--session', default='global')

    def do_command(self):
        manager = DatastoreManager(self.client)
        clip4_datastore = manager.open_or_create_datastore(program_name)
        clip4_table = clip4_datastore.get_table(self.args.session)
        # print("YMK get args {0}".format(self.args))
        buffers = list(clip4_table.query())
        if len(buffers) != 0:
            for buf in buffers:
                print("{0} {1} [{2}]".format(buf.get('index'),
                                             buf.get('date'), buf.get('buffer')))


class command_set(command):
    " clip4 command 'set' """

    @staticmethod
    def add_sub_command(sub_par):
        cmdparser = sub_par.add_parser('set')
        cmdparser.add_argument('-s', '--session', default='global')
        cmdparser.add_argument('-i', '--index', type=int, default=0)
        cmdparser.add_argument('content')

    def do_command(self):
        manager = DatastoreManager(self.client)
        clip4_datastore = manager.open_or_create_datastore(program_name)
        clip4_table = clip4_datastore.get_table(self.args.session)
        # print("YMK get args {0}".format(self.args))
        now = datetime.datetime.utcnow()
        buffers = list(clip4_table.query(index=self.args.index))
        if len(buffers) == 0:
            clip4_table.insert(index=self.args.index, buffer=self.args.content,
                               date=Date.from_datetime_utc(now))
        else:
            buffers[0].update(buffer=self.args.content, date=Date.from_datetime_utc(now))
        clip4_datastore.commit()


class command_clear(command):
    " clip4 command 'clear' """

    @staticmethod
    def add_sub_command(sub_par):
        cmdparser = sub_par.add_parser('clear')
        cmdparser.add_argument('-s', '--session', default='global')
        cmdparser.add_argument('-i', '--index', type=int, default=0)
        cmdparser.add_argument('-a', '--all', action='store_true')

    def do_command(self):
        manager = DatastoreManager(self.client)
        clip4_datastore = manager.open_or_create_datastore(program_name)
        clip4_table = clip4_datastore.get_table(self.args.session)
        # print("YMK get args {0}".format(self.args))
        if self.args.all:
            buffers = list(clip4_table.query())
        else:
            buffers = list(clip4_table.query(index=self.args.index))
        for buf in buffers:
            buf.delete_record()
        clip4_datastore.commit()


def get_dropbox_token():
    APP_KEY = 'dundvtx4d2z9ond'
    APP_SECRET = '6vdzi99zwy8dsfa'
    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    authorize_url = auth_flow.start()
    webbrowser.open_new_tab(authorize_url)
    try:
        auth_code = input("Enter the authorization code here: ").strip()
        access_token, user_id = auth_flow.finish(auth_code)
    except dbrest.ErrorResponse as e:
        sys.exit('Error: %s' % (e,))
    except KeyboardInterrupt:
        sys.exit('Error: KeyboardInterrupt')

    return access_token


def get_dropbox_client(token=None):
    if token is None:
        access_token = get_dropbox_token()
    else:
        access_token = token

    return DropboxClient(access_token)


def test_insert(datastore, table, index):
    now = datetime.datetime.utcnow()
    table.insert(index=index, buffer=str(now), date=Date.from_datetime_utc(now))
    if datastore is not None:
        datastore.commit()


def main():
    # argparser
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('-p', '--profile', default='default')
    subparser = parser.add_subparsers(dest='command_name')

    # commands classes
    command_classes = {'get': command_get,
                       'set': command_set,
                       'list': command_list,
                       'clear': command_clear}
    for val in command_classes.values():
        val.add_sub_command(subparser)

    args = parser.parse_args()

    # load configs
    config = configparser.RawConfigParser()
    config_paths = ['~/.config/', './']
    last_cfg_name = ""
    for cfg_path in config_paths:
        cfg_name = os.path.expanduser(cfg_path + '.' + program_name + 'rc')
        if os.path.exists(cfg_name):
            last_cfg_name = cfg_name
            config.read(cfg_name)

    # token = 'HBfujyMbh6MAAAAAAAACAB-1qIulPmBdQHqasXeGN5CTVId6by4cLCYpKlOkA4xu'
    token = config.get('default', 'access_token', fallback=None)
    if last_cfg_name == "":
        token = get_dropbox_token()
        config['default'] = {'access_token': token}
        with open(os.path.expanduser(
                config_paths[0] + '.' + program_name + 'rc'), 'w') as cfg_file:
            config.write(cfg_file)
    client = get_dropbox_client(token)

    # command instances
    if args.command_name is not None:
        command = command_classes[args.command_name](client)
        command(args)

    # client = get_dropbox_client(token)

    # datastore
    # manager = DatastoreManager(client)

    # datastores = manager.list_datastores()
    # for ds in datastores:
    #    print("datastore {0}".format(ds))
    # print("default datastore valid:{0} shared:{1}".format(Datastore.is_valid_id(datastore.get_id()),
    #                                                      Datastore.is_valid_shareable_id(datastore.get_id())))

    # reset/delete clip4_datastore
    # manager.delete_datastore('clip4')

    # clip4_datastore = manager.open_or_create_datastore('clip4')
    # clip4_table = clip4_datastore.get_table('global')

    # add some buffer in clip4
    # for id in range(4):
    #    clip4_datastore.transaction(test_insert, clip4_datastore, clip4_table, id, max_tries=4)

    # get all buffers
    # buffers = clip4_table.query()
    # for buffer in buffers:
    #    print("buffer: {0}, datetime {1} [{2}]".format(buffer.get('index'),
    #                                                    buffer.get('date'),
    #                                                    buffer.get('buffer')))

    # query buffer
    # buffers = list(clip4_table.query(index=0))
    # print(buffers[0].get('buffer'))


if __name__ == "__main__":
    main()
