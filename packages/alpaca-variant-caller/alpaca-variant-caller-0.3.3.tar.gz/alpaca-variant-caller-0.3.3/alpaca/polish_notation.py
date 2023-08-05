

def parse_tokens(tokens, is_operator):
    if is_operator(tokens[0]):
        return parse_tokens(
            list(takewhile(lambda token: not is_operator(token), tokens[1:]))
