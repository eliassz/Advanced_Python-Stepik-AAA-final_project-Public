import random
from typing import List

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from tic_tac_toe_bot.utils import (
    CONTINUE_GAME,
    CROSS,
    FINISH_GAME,
    FREE_SPACE,
    ZERO,
    generate_keyboard,
    get_default_state,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data["keyboard_state"] = get_default_state()
    keyboard = generate_keyboard(context.user_data["keyboard_state"])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "X your turn! Please, put X to the free place", reply_markup=reply_markup
    )
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # Extract the row and column from the callback data
    row, col = int(query.data[0]), int(query.data[1])
    board = context.user_data["keyboard_state"]

    # Player's move
    if board[row][col] != FREE_SPACE:
        await query.edit_message_text("Space is already taken, choose another one.")
        return CONTINUE_GAME

    board[row][col] = CROSS

    # Check for player win or tie
    if won(board):
        await query.edit_message_text("Congratulations! You have won!")
        return FINISH_GAME
    elif all(all(cell != FREE_SPACE for cell in row) for row in board):
        await query.edit_message_text("It's a tie!")
        return FINISH_GAME

    # Opponent's move (random)
    empty_cells = [
        (r, c) for r in range(3) for c in range(3) if board[r][c] == FREE_SPACE
    ]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = ZERO

        # Check for opponent win or tie after their move
        if won(board):
            await query.edit_message_text("Sorry, you lost!")
            return FINISH_GAME
        elif all(all(cell != FREE_SPACE for cell in row) for row in board):
            await query.edit_message_text("It's a tie!")
            return FINISH_GAME

    # Update the board and ask for the next move
    keyboard = generate_keyboard(board)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Your turn! Please, put X to the free place", reply_markup=reply_markup
    )
    return CONTINUE_GAME


def won(board: List[List[str]]) -> bool:
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != FREE_SPACE:
            return True

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != FREE_SPACE:
            return True

    # Check diagonals
    if (
        board[0][0] == board[1][1] == board[2][2] != FREE_SPACE
        or board[0][2] == board[1][1] == board[2][0] != FREE_SPACE
    ):
        return True

    return False


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    # reset state to default so you can play again with /start
    context.user_data["keyboard_state"] = get_default_state()
    return ConversationHandler.END
