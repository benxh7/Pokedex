from core.models import Comentario
from api.schemas import CommentaryOut, UserOut

def serialize_user(u) -> UserOut:
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        date_joined=u.date_joined,
        date_joined_ts=int(u.date_joined.timestamp()),
        is_superuser=u.is_superuser
    )

def serialize_comment(c: Comentario) -> CommentaryOut:
    return CommentaryOut(
        id=c.id,
        content=c.content,
        usuario=c.usuario.username,
        created=c.created,
        updated=c.updated,
        parent=c.parent_id,
        replies=[serialize_comment(r) for r in c.replies.all().order_by("created")]
    )