from django.db import models
import uuid


def generate_room_id():
    new_uuid = uuid.uuid4().hex[:16].upper()
    if Room.objects.filter(room_id=new_uuid).exists():
        new_uuid = generate_room_id()
    return new_uuid

class Room(models.Model):

    room_id = models.CharField(max_length=16, unique=True, default=generate_room_id)
    player_a = models.CharField(max_length=50, null=True, blank=True)
    player_a_color = models.CharField(max_length=5, null=True, blank=True)

    player_b = models.CharField(max_length=50, null=True, blank=True)
    player_b_color = models.CharField(max_length=5, null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=[
            ("WAITING", "Waiting"),
            ("ACTIVE", "Active"),
            ("FINISHED", "Finished"),
        ],
        default="WAITING",
    )
    active = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(auto_now=True)

    winner = models.CharField(max_length=10, null=True, blank=True, default="Unknown")

    def __str__(self):
        return f"Room {self.room_id}"


class Match(models.Model):
    board = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=50, null=True, blank=True)
