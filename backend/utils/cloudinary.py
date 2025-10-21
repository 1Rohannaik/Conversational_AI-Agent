from dotenv import load_dotenv
import os
import cloudinary

# Load .env so either CLOUDINARY_URL or individual vars are available
load_dotenv()


def _configure_from_env() -> None:
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    if cloudinary_url:
        cloudinary.config(cloudinary_url=cloudinary_url, secure=True)
    else:
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        if cloud_name and api_key and api_secret:
            cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)


def ensure_configured() -> None:
    """Ensure Cloudinary is configured from environment or raise RuntimeError."""
    _configure_from_env()
    cfg = cloudinary.config()
    if not (cfg.api_key and cfg.api_secret and cfg.cloud_name):
        raise RuntimeError(
            "Cloudinary is not configured: set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET in env"
        )

