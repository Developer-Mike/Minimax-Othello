import server

server.start({})

is_game_over = False
while not is_game_over:
    # Play AI vs AI
    response = server.ai_move({})
    print(response["board"])

    # Check if move is available
    is_game_over = response["move"]["x"] == -1