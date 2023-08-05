# -*- coding: utf-8 -*-

import functools
import json

from .utils import CliError, JobFailed, cli_logger, collections_for_pair, \
    get_status_name, handle_cli_error, load_status, save_status, \
    storage_instance_from_config

from ..sync import sync


def sync_pair(wq, pair_name, collections_to_sync, general, all_pairs,
              all_storages, force_delete):
    key = ('prepare', pair_name)
    if key in wq.handled_jobs:
        cli_logger.warning('Already prepared {}, skipping'.format(pair_name))
        return
    wq.handled_jobs.add(key)

    a_name, b_name, pair_options = all_pairs[pair_name]

    all_collections = dict(collections_for_pair(
        general['status_path'], a_name, b_name, pair_name,
        all_storages[a_name], all_storages[b_name], pair_options
    ))

    # spawn one worker less because we can reuse the current one
    new_workers = -1
    for collection in (collections_to_sync or all_collections):
        try:
            config_a, config_b = all_collections[collection]
        except KeyError:
            raise CliError('Pair {}: Collection {} not found. These are the '
                           'configured collections:\n{}'.format(
                               pair_name, collection, list(all_collections)))
        new_workers += 1
        wq.put(functools.partial(
            sync_collection, pair_name=pair_name, collection=collection,
            config_a=config_a, config_b=config_b, pair_options=pair_options,
            general=general, force_delete=force_delete
        ))

    for i in range(new_workers):
        wq.spawn_worker()


def sync_collection(wq, pair_name, collection, config_a, config_b,
                    pair_options, general, force_delete):
    status_name = get_status_name(pair_name, collection)

    key = ('sync', pair_name, collection)
    if key in wq.handled_jobs:
        cli_logger.warning('Already syncing {}, skipping'.format(status_name))
        return
    wq.handled_jobs.add(key)

    try:
        cli_logger.info('Syncing {}'.format(status_name))

        status = load_status(general['status_path'], pair_name,
                             collection, data_type='items') or {}
        cli_logger.debug('Loaded status for {}'.format(status_name))

        a = storage_instance_from_config(config_a)
        b = storage_instance_from_config(config_b)
        sync(
            a, b, status,
            conflict_resolution=pair_options.get('conflict_resolution', None),
            force_delete=force_delete
        )
    except:
        handle_cli_error(status_name)
        raise JobFailed()

    save_status(general['status_path'], pair_name, collection,
                data_type='items', data=status)


def discover_collections(wq, pair_name, **kwargs):
    rv = collections_for_pair(pair_name=pair_name, **kwargs)
    collections = list(c for c, (a, b) in rv)
    if collections == [None]:
        collections = None
    cli_logger.info('Saved for {}: collections = {}'
                    .format(pair_name, json.dumps(collections)))
