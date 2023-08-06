"""Tests for the experimentator workflow.

Tests the process of creating an experiment, pickling it to disk, running command-line operations on it, and unpickling
it.

"""
import sys
import os
import filecmp
from glob import glob
from contextlib import contextmanager
from numpy import isnan
import pytest

from experimentator import run_experiment_section, QuitSession, Experiment, DesignTree, Design
from experimentator.design import Level
from experimentator.__main__ import main
from experimentator.order import Ordering
from tests.test_experiment import make_blocked_exp, check_trial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def call_cli(args):
    main(args=args.split()[1:])


def set_session_data(experiment, section):
    experiment.session_data['test'] = True


def check_session_data(experiment, section):
    assert experiment.session_data['test']


@contextmanager
def participant_context(experiment, section):
    experiment.session_data['test'] = True
    yield


@contextmanager
def block_context(experiment, section):
    if section.data['block'] > 1:
        assert experiment.session_data['test']
    yield


def test_cli():
    exp = make_blocked_exp()
    exp.set_context_manager('participant', participant_context)
    exp.set_context_manager('block', block_context)
    exp.filename = 'test.pkl'
    exp.save()

    call_cli('exp run test.pkl --next participant')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] == 1:
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp --demo run test.pkl participant 2 block 1')
    for row in exp.dataframe.iterrows():
        if row[0][0] == 1:
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp run test.pkl participant 2 block 1')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] == 1 or (row[0][0] == 2 and row[0][1] == 1):
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp resume test.pkl participant')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] <= 2:
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp run test.pkl --next trial')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] <= 2 or row[0] == (3, 1, 1):
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp resume test.pkl participant 3 block 1 --demo')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] <= 2 or row[0] == (3, 1, 1):
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp --debug resume test.pkl participant 3 block 1')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] <= 2 or row[0][:2] == (3, 1):
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp run test.pkl participant 3 block 3 --from 3')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if row[0][0] <= 2 or row[0][:2] == (3, 1) or (row[0][:2] == (3, 3) and row[0][-1] >= 3):
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    call_cli('exp run test.pkl participant 3 --from 2,4')
    exp = Experiment.load('test.pkl')
    for row in exp.dataframe.iterrows():
        if (row[0][0] <= 2
                or row[0][:2] == (3, 1)
                or (row[0][:2] == (3, 2) and row[0][-1] >= 4)
                or (row[0][:2] == (3, 3) and row[0][2] > 2)):
            yield check_trial, row
        else:
            assert isnan(row[1]['result'])

    for file in glob('test.pkl*'):
        os.remove(file)


def test_pickle_error():
    exp = make_blocked_exp()
    exp.set_context_manager('block', block_context, func_module='not_a_module')
    exp.filename = 'test.pkl'
    exp.save()

    with pytest.raises(ImportError):
        call_cli('exp run test.pkl --next participant')


@contextmanager
def context(experiment, section):
    assert experiment.session_data['options'] == 'pass,through,option'
    yield


def test_options():
    exp = make_blocked_exp()
    exp.set_context_manager('block', context)
    exp.filename = 'test.pkl'
    exp.save()
    call_cli('exp run test.pkl --next participant -o pass,through,option')


def make_deterministic_exp():
    Experiment.basic(('participant', 'block', 'trial'),
                     {'block': {'b': [0, 1, 2]}, 'trial': {'a': [False, True]}},
                     ordering_by_level={'trial': Ordering(4),
                                        'block': Ordering(4),
                                        'participant': Ordering()},
                     filename='test.pkl').save()


def test_export():
    make_deterministic_exp()
    call_cli('exp export test.pkl test.csv')
    assert (filecmp.cmp('tests/test_data.csv', 'test.csv')
            or filecmp.cmp('tests/test_data_alt.csv', 'test.csv'))
    os.remove('test.csv')

    call_cli('exp export --no-index-label test.pkl test.csv')
    assert (filecmp.cmp('tests/test_data_no_index_label.csv', 'test.csv')
            or filecmp.cmp('tests/test_data_no_index_label_alt.csv', 'test.csv'))
    os.remove('test.csv')

    call_cli('exp export test.pkl test.csv --skip counterbalance_order')
    assert (filecmp.cmp('tests/test_data_skip_order.csv', 'test.csv')
            or filecmp.cmp('tests/test_data_skip_order_alt.csv', 'test.csv'))
    os.remove('test.csv')

    for file in glob('test.pkl*'):
        os.remove(file)


def bad_trial(experiment, section):
    raise QuitSession('Nope!')


def test_exception():
    exp = make_blocked_exp()
    exp.set_run_callback(bad_trial)
    exp.save()
    exp.save('test.pkl')
    with pytest.raises(QuitSession):
        run_experiment_section('test.pkl', participant=1)

    exp = Experiment.load('test.pkl')
    assert exp.subsection(participant=1, block=1, trial=1).has_started
    assert not exp.subsection(participant=1, block=1, trial=1).has_finished
    os.remove('test.pkl')

    e = QuitSession('message')
    assert e.__str__() == 'message'
    with pytest.raises(QuitSession):
        raise e


def test_exp_repr():
    make_deterministic_exp()
    e = Experiment.load('test.pkl')
    assert e == eval(repr(e))
    for file in glob('test.pkl*'):
        os.remove(file)
