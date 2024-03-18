"""
Bot for playing tic tac toe game with multiple CallbackQueryHandlers.
"""
import logging
import os
import random
from copy import deepcopy
from typing import List

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# get token using BotFather
TOKEN = os.getenv("TG_TOKEN")

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = "."
CROSS = "X"
ZERO = "O"


DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state():
    """Helper function to get default state of the game"""
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: List[List[str]]) -> List[List[InlineKeyboardButton]]:
    """Generate tic tac toe keyboard 3x3 (telegram buttons)"""
    return [
        [InlineKeyboardButton(state[r][c], callback_data=f"{r}{c}") for r in range(3)]
        for c in range(3)
    ]


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


def main() -> None:
    """Run the bot"""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states CONTINUE_GAME and FINISH_GAME
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern="^" + f"{r}{c}" + "$")
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern="^" + f"{r}{c}" + "$")
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
