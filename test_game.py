from main import won, get_default_state


def test_won():
    # Test a winning row
    board1 = [['X', 'X', 'X'], ['O', 'O', '.'], ['.', '.', '.']]
    assert won(board1) == True

    # Test a winning column
    board2 = [['X', 'O', 'O'], ['X', '.', 'O'], ['X', '.', '.']]
    assert won(board2) == True

    # Test a winning diagonal
    board3 = [['X', 'O', 'O'], ['O', 'X', 'O'], ['.', '.', 'X']]
    assert won(board3) == True

    # Test no winner
    board4 = [['X', 'O', 'X'], ['O', 'X', 'O'], ['O', 'X', 'O']]
    assert won(board4) == False

def test_get_default_state():
    default_state = get_default_state()
    assert len(default_state) == 3
    assert len(default_state[0]) == 3
    assert all(all(cell == '.' for cell in row) for row in default_state)
