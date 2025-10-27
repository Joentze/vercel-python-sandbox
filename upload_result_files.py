"""Upload result files to Vercel Blob storage."""
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from vercel.blob import AsyncBlobClient, UploadProgressEvent


# Load environment variables
if not load_dotenv('.env.local'):
    load_dotenv()


def on_progress(_: UploadProgressEvent) -> None:
    # Silent progress tracking
    pass


async def upload_file(client: AsyncBlobClient, filepath: Path) -> dict:
    """Upload a single file to Vercel Blob storage."""
    filename = filepath.name

    # Read file bytes
    with open(filepath, 'rb') as f:
        file_bytes = f.read()

    # Upload to Vercel Blob
    blob = await client.put(
        f"results/{filename}",
        file_bytes,
        access="public",
        add_random_suffix=True,
        on_upload_progress=on_progress,
    )

    return {
        "url": blob.url,
        "pathname": blob.pathname,
        "filename": filename,
    }


async def upload_all_results() -> None:
    """Check for files in ./results and upload them."""
    results_dir = Path("./results")

    # Check if results directory exists
    if not results_dir.exists():
        print("No files found in './results' directory.")
        return

    # Get all files in the results directory
    files = [f for f in results_dir.iterdir() if f.is_file()]

    if not files:
        print("No files found in './results' directory.")
        return

    # Initialize Vercel Blob client
    client = AsyncBlobClient()

    # Upload each file
    uploaded_files = []
    for filepath in files:
        try:
            result = await upload_file(client, filepath)
            uploaded_files.append(result)
        except Exception:
            # Silently skip failed uploads
            pass

    # Print results in markdown format
    if uploaded_files:
        print("# Uploaded Files\n")
        for file_info in uploaded_files:

            print(f"[{file_info['filename']}]({file_info['url']})")
            print(f"  - **Pathname**: `{file_info['pathname']}`\n")
    else:
        print("No files found in './results' directory.")


if __name__ == "__main__":
    asyncio.run(upload_all_results())
