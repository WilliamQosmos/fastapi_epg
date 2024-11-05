import io
from pathlib import Path

from PIL import Image
from sqlalchemy import update

from app.core.db import AsyncSessionFactory
from app.models.user import User


async def add_watermark(image: bytes, filename: str, user_email: str):
    watermark = Image.open(Path(__file__).parent.parent.parent / "static" / "watermark.png")
    image = Image.open(io.BytesIO(image))
    width, height = image.size
    transparent = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    transparent.paste(image, (0, 0))
    transparent.paste(watermark, (width - watermark.size[0], height - watermark.size[1]), mask=watermark)
    transparent.convert("RGB").save(Path(__file__).parent.parent.parent / "static" / filename)
    async with AsyncSessionFactory() as session:
        await session.execute(update(User).where(User.email == user_email).values(avatar=filename))
        await session.commit()
