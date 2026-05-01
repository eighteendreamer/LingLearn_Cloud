from sqlalchemy.dialects import mysql

from app.modules.content.models import ContentFavorite, ContentItem
from app.modules.content.repository import ContentRepository


def test_favorites_query_compiles_with_viewer_favorite_alias() -> None:
    repository = ContentRepository()
    stmt = (
        repository._build_content_row_stmt(viewer_user_id=1)
        .add_columns(ContentFavorite.created_at.label("favorited_at"))
        .join(ContentFavorite, ContentFavorite.content_item_id == ContentItem.id)
        .where(ContentFavorite.user_id == 1, *repository._public_content_conditions())
        .order_by(ContentFavorite.created_at.desc(), ContentFavorite.id.desc())
        .offset(0)
        .limit(6)
    )

    compiled = str(stmt.compile(dialect=mysql.dialect()))

    assert "content_favorites AS content_favorites_1" in compiled
