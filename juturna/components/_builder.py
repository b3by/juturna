import os
import tomllib
import importlib
import importlib.resources

from juturna.utils.log_utils import jt_logger
from juturna.utils.jt_utils._get_env_var import get_env_var
from juturna.meta._constants import JUTURNA_ENV_VAR_PREFIX
from juturna.components._synchronisers import _SYNCHRONISERS


_JT_EXT_PREFIX = 'juturna.'

_logger = jt_logger('builder')


def build_node(node: dict, pipe_name: str):
    node_full_path = node['type']
    node_name = node_full_path.split('.')[-1]
    node_sync = node.get('sync')
    node_configuration = node['configuration']
    node_class, default_config = _resolve_node(node_full_path)
    default_args = default_config['arguments']

    operational_config = _update_local_with_remote(
        default_args, node_configuration
    )

    items_to_process = [
        (key, value)
        for key, value in operational_config.items()
        if isinstance(value, str)
        and value.startswith(JUTURNA_ENV_VAR_PREFIX)
        and key in default_args
    ]

    operational_config.update(
        {
            key: _resolve_env_var(key, value, node_name, default_args)
            for key, value in items_to_process
        }
    )

    synchroniser = _SYNCHRONISERS.get(node_sync)
    concrete_node = node_class(
        **operational_config,
        **{
            'node_name': node_name,
            'pipe_name': pipe_name,
            'synchroniser': synchroniser,
        },
    )

    concrete_node.configure()

    return concrete_node


def _resolve_node(node_full_path: str) -> str:
    node_name = node_full_path.split('.')[-1]
    node_path = '.'.join(node_full_path.split('.')[:-1])

    if node_path.split('.')[0] in ['extensions', 'contrib']:
        node_path = _JT_EXT_PREFIX + node_path
    else:
        node_path = _JT_EXT_PREFIX + 'nodes.' + node_path

    node_module = importlib.import_module(node_path)
    node_class = getattr(node_module, node_name)
    config_file_path = (
        importlib.resources.files(node_class.__module__) / 'config.toml'
    )

    with open(config_file_path, 'rb') as f:
        default_config = tomllib.load(f)

    return node_class, default_config


def _update_local_with_remote(local: dict, remote: dict) -> dict:
    merged_config = {k: remote.get(k, v) for k, v in local.items()}

    return merged_config


def _resolve_env_var(
    key: str, value: str, node_name: str, local_arguments: dict
) -> str:
    env_var_name = value[len(JUTURNA_ENV_VAR_PREFIX) :]
    default_value = local_arguments[key]

    if env_var_name not in os.environ:
        error_msg = (
            f'env variable "{env_var_name}" is not set in node "{node_name}" '
            f'for config key "{key}" (found in config but not in environment)'
        )
        _logger.error(error_msg)
        raise ValueError(error_msg)

    return get_env_var(env_var_name, default_value)
