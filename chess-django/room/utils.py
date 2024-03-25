import uuid

# Generate a unique room ID
def generate_room_id():
    return uuid.uuid4().hex[:6].upper()