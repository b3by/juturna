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
