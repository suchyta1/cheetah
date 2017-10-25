import os.path
import shutil
import json

from nose.tools import assert_equal

from codar.cheetah.model import Campaign, NodeLayout
from codar.cheetah.parameters import SweepGroup, Sweep, ParamCmdLineArg

from test_cheetah import TEST_OUTPUT_DIR


class TestCampaign(Campaign):
    name = 'test_campaign'
    supported_machines = ['local', 'titan', 'cori']
    codes = [('test', dict(exe='test'))]
    sweeps = [
        SweepGroup(name='test_group', nodes=1, parameter_groups=[
          Sweep([ParamCmdLineArg('test', 'arg', 1, ['a', 'b'])])
        ])
    ]


def test_bad_scheduler_options():
    class BadCampaign(TestCampaign):
        name = 'bad_scheduler_options'
        scheduler_options = { 'titan': dict(notanoption='test') }

    try:
        c = BadCampaign('titan', '/test')
    except ValueError as e:
        assert 'notanoption' in str(e), "Bad error message: " + str(e)
    else:
        assert False, 'expected ValueError from bad option'


def test_default_scheduler_options():
    class DefaultOptionCampaign(TestCampaign):
        name = 'default_options'
        # Alternate license option, use default constraint and queue
        scheduler_options = { 'cori': dict(license='SCRATCH') }

    c = DefaultOptionCampaign('cori', '/test')
    assert_equal(c.machine_scheduler_options['license'], 'SCRATCH')
    assert_equal(c.machine_scheduler_options['constraint'], 'haswell')
    assert_equal(c.machine_scheduler_options['queue'], 'debug')


def test_codes_ordering():
    class TestMultiExeCampaign(TestCampaign):
        codes = [('first', dict(exe='testa')),
                 ('second', dict(exe='testb')),
                 ('third', dict(exe='testc')),
                 ('fourth', dict(exe='testd')),
                 ('fifth', dict(exe='teste')),
                 ('sixth', dict(exe='testf')),
                 ('seventh', dict(exe='testg'))]
        sweeps = [
            SweepGroup(name='test_group', nodes=1, parameter_groups=[
              Sweep([
                ParamCmdLineArg('first', 'arg', 1, ['a', 'b']),
                ParamCmdLineArg('second', 'arg', 1, ['2']),
                ParamCmdLineArg('third', 'arg', 1, ['3']),
                ParamCmdLineArg('fourth', 'arg', 1, ['4']),
                ParamCmdLineArg('fifth', 'arg', 1, ['5', 'five']),
                ParamCmdLineArg('sixth', 'arg', 1, ['6']),
                ParamCmdLineArg('seventh', 'arg', 1, ['7']),
              ])
            ])
        ]

    c = TestMultiExeCampaign('titan', '/test')
    out_dir = os.path.join(TEST_OUTPUT_DIR,
                           'test_model', 'test_codes_ordering')
    fob_path = os.path.join(out_dir, 'test_group', 'fobs.json')
    shutil.rmtree(out_dir, ignore_errors=True) # clean up any old test output
    c.make_experiment_run_dir(out_dir)

    correct_order = list(c.codes.keys())

    fobs = []
    with open(fob_path) as f:
        for line in f:
            fobs.append(json.loads(line))

    for fob in fobs:
        fob_order = [run['name'] for run in fob['runs']]
        assert_equal(fob_order, correct_order)


def test_node_layout_repeated_code():
    layout = [{ 'stage': 3, 'heat': 10}, { 'ds': 1, 'heat': 5 }]
    try:
        nl = NodeLayout(layout)
    except ValueError as e:
        assert 'heat' in str(e), str(e)
    else:
        assert False, 'error not raised on repeated code'


def test_node_layout_bad_ppn():
    layout = [{ 'stage': 3, 'heat': 10}, { 'ds': 12 }]
    nl = NodeLayout(layout)
    try:
        nl.validate(12, 2, 2)
    except ValueError as e:
        assert 'ppn > max' in str(e), str(e)
    else:
        assert False, 'error not raised on repeated code'


def test_node_layout_bad_codes_per_node():
    layout = [{ 'stage': 3, 'core': 4, 'edge': 4 }, { 'ds': 12 }]
    nl = NodeLayout(layout)
    try:
        nl.validate(12, 2, 2)
    except ValueError as e:
        assert 'codes > max' in str(e), str(e)
    else:
        assert False, 'error not raised on repeated code'


def test_node_layout_bad_shared_nodes():
    layout = [{ 'stage': 3, 'core': 4, 'edge': 4 }, { 'ds': 10, 'heat': 5 }]
    nl = NodeLayout(layout)
    try:
        nl.validate(24, 4, 1)
    except ValueError as e:
        assert 'shared nodes > max' in str(e), str(e)
    else:
        assert False, 'error not raised on repeated code'