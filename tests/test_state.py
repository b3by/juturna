from juturna.components import State


def test_state_accessors():
    state = State()

    state['key_a'] = 10
    state['key_b'] = 20

    assert state['key_a'] == 10
    assert state['key_b'] == 20

    del state['key_a']

    assert 'key_a' not in state
    assert 'key_b' in state


def test_state_initial_deltas():
    state = State()

    assert state.deltas() == list()


def test_state_deltas():
    state = State()

    state['key_a'] = 10
    state['key_b'] = 20

    deltas = state.deltas()

    assert ('SET', 'key_a', 10) in deltas
    assert ('SET', 'key_b', 20) in deltas

    assert state.deltas() == list()


def test_state_delta_overwrite():
    state = State()

    state['key_a'] = 10

    assert state.deltas() == [('SET', 'key_a', 10)]
    assert state.deltas() == list()

    state['key_a'] = 20
    state['key_a'] = 30

    assert state.deltas() == [('SET', 'key_a', 30)]
    assert state.deltas() == list()

    state['key_a'] = 40
    del state['key_a']

    assert state.deltas() == [('DEL', 'key_a', None)]
    assert state.deltas() == list()
