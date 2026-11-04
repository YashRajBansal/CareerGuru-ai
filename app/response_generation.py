"""Legacy import compatibility. MongoDB is no longer needed by Career Guru."""
from services.ai import complete, SAFETY

def get_or_generate_response(user_query, chatbot_type=None):
    return complete(SAFETY, user_query)

def get_response_from_db(user_query, chatbot_type=None):
    return get_or_generate_response(user_query, chatbot_type)

def store_query_response(query, response, chatbot_type=None):
    # The authenticated /api/chat route owns persistent history and review logging.
    raise RuntimeError('Use the authenticated Career Guru chat API to persist conversations.')
