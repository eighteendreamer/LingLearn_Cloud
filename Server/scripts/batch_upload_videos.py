from __future__ import annotations

import argparse
import json
import mimetypes
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_SOURCE_DIR = Path(r"F:\xiaz\智慧学习平台1 (2)\智慧学习平台1\videos")
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}


@dataclass
class AccountSeed:
    username: str
    email: str
    password: str
    display_name: str


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def post_json(self, path: str, payload: dict[str, Any], token: str | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req = request.Request(
            url=f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method="POST",
        )
        return self._send_json(req)

    def put_binary(self, url: str, data: bytes, headers: dict[str, str] | None = None) -> dict[str, Any]:
        req = request.Request(url=url, data=data, method="PUT")
        for key, value in (headers or {}).items():
            req.add_header(key, value)

        with request.urlopen(req) as response:
            etag = response.headers.get("ETag", "").strip()
            return {
                "status": response.status,
                "etag": etag.strip('"'),
            }

    @staticmethod
    def _send_json(req: request.Request) -> dict[str, Any]:
        try:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
            raise RuntimeError(f"HTTP {exc.code}: {json.dumps(data, ensure_ascii=False)}") from exc


def build_accounts(prefix: str, count: int, password: str) -> list[AccountSeed]:
    return [
        AccountSeed(
            username=f"{prefix}_{index:02d}",
            email=f"{prefix}_{index:02d}@example.com",
            password=password,
            display_name=f"{prefix.upper()} {index:02d}",
        )
        for index in range(1, count + 1)
    ]


def login_or_register(client: ApiClient, account: AccountSeed) -> str:
    try:
        client.post_json(
            "/auth/register",
            {
                "username": account.username,
                "email": account.email,
                "password": account.password,
                "display_name": account.display_name,
            },
        )
        print(f"[account] registered {account.username}")
    except RuntimeError as exc:
        message = str(exc)
        if "409" not in message and "conflict" not in message.lower() and "已存在" not in message:
            raise
        print(f"[account] already exists, login directly: {account.username}")

    login_response = client.post_json(
        "/auth/login",
        {
            "account": account.username,
            "password": account.password,
            "device_id": "batch-upload-script",
        },
    )
    token_data = extract_response_data(login_response)
    print(f"[account] login ok: {account.username}")
    return str(token_data["access_token"])


def extract_response_data(response: dict[str, Any]) -> dict[str, Any]:
    if response.get("code") != 0:
        raise RuntimeError(f"API error: {json.dumps(response, ensure_ascii=False)}")
    data = response.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response data: {json.dumps(response, ensure_ascii=False)}")
    return data


def choose_assignments(
    videos: list[Path],
    accounts: list[AccountSeed],
    *,
    min_videos: int,
    max_videos: int,
    seed: int,
) -> dict[str, list[Path]]:
    if not videos:
        raise RuntimeError("No video files found.")

    rng = random.Random(seed)
    shuffled = videos[:]
    rng.shuffle(shuffled)

    assignments: dict[str, list[Path]] = {}
    cursor = 0
    for account in accounts:
        planned_count = rng.randint(min_videos, max_videos)
        picked: list[Path] = []
        for _ in range(planned_count):
            picked.append(shuffled[cursor % len(shuffled)])
            cursor += 1
        assignments[account.username] = picked
    return assignments


def upload_video(
    client: ApiClient,
    *,
    token: str,
    file_path: Path,
) -> int:
    mime_type = mimetypes.guess_type(file_path.name)[0] or "video/mp4"
    file_size = file_path.stat().st_size

    init_response = client.post_json(
        "/storage/initiate-multipart-upload",
        {
            "biz_type": "content_video",
            "file_name": file_path.name,
            "file_size": file_size,
            "mime_type": mime_type,
        },
        token=token,
    )
    init_data = extract_response_data(init_response)
    asset_id = int(init_data["asset_id"])
    upload_id = str(init_data["upload_id"])
    part_size = int(init_data["part_size"])
    part_count = int(init_data["part_count"])

    print(f"[upload] {file_path.name} asset_id={asset_id} parts={part_count}")

    parts: list[dict[str, Any]] = []
    with file_path.open("rb") as file_handle:
        for part_number in range(1, part_count + 1):
            chunk = file_handle.read(part_size)
            if not chunk:
                break

            sign_response = client.post_json(
                "/storage/presign-upload-part",
                {
                    "asset_id": asset_id,
                    "upload_id": upload_id,
                    "part_number": part_number,
                },
                token=token,
            )
            sign_data = extract_response_data(sign_response)
            put_result = client.put_binary(
                url=str(sign_data["upload_url"]),
                data=chunk,
                headers={str(key): str(value) for key, value in dict(sign_data.get("headers") or {}).items()},
            )
            parts.append({"part_number": part_number, "etag": put_result["etag"]})
            print(f"  - part {part_number}/{part_count} uploaded")

    complete_response = client.post_json(
        "/storage/complete-multipart-upload",
        {
            "asset_id": asset_id,
            "upload_id": upload_id,
            "parts": parts,
        },
        token=token,
    )
    extract_response_data(complete_response)
    return asset_id


def create_content(
    client: ApiClient,
    *,
    token: str,
    video_asset_id: int,
    file_path: Path,
    category_id: int | None,
) -> dict[str, Any]:
    title = normalize_title(file_path.stem)
    hashtags = build_hashtags(file_path.stem)

    create_response = client.post_json(
        "/contents",
        {
            "title": title[:120],
            "summary": f"批量导入视频：{title}"[:500],
            "category_id": category_id,
            "cover_asset_id": None,
            "primary_media_asset_id": video_asset_id,
            "content_type": "short_video",
            "hashtags": hashtags[:20],
            "allow_comment": True,
            "allow_duet": False,
        },
        token=token,
    )
    return extract_response_data(create_response)


def normalize_title(raw_name: str) -> str:
    title = re.sub(r"[_\-]+", " ", raw_name).strip()
    title = re.sub(r"\s+", " ", title)
    return title or "批量导入视频"


def build_hashtags(raw_name: str) -> list[str]:
    parts = re.split(r"[_\-\s]+", raw_name)
    cleaned = []
    for part in parts:
        item = part.strip()
        if not item:
            continue
        if len(item) > 20:
            item = item[:20]
        cleaned.append(item)
    cleaned.append("批量上传")
    seen: set[str] = set()
    result: list[str] = []
    for tag in cleaned:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result


def list_videos(source_dir: Path) -> list[Path]:
    return sorted(
        file_path
        for file_path in source_dir.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch register users and upload videos to LingLearn Cloud.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8003/api/v1", help="Backend API base URL.")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR), help="Directory containing video files.")
    parser.add_argument("--account-prefix", default="seeduser", help="Username/email prefix for generated accounts.")
    parser.add_argument("--account-count", type=int, default=4, help="How many accounts to generate.")
    parser.add_argument("--password", default="SeedUser123", help="Shared password for generated accounts.")
    parser.add_argument("--min-videos", type=int, default=2, help="Minimum videos per account.")
    parser.add_argument("--max-videos", type=int, default=3, help="Maximum videos per account.")
    parser.add_argument("--category-id", type=int, default=None, help="Optional content category ID.")
    parser.add_argument("--seed", type=int, default=20260430, help="Random seed used for assignment.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"[error] source dir not found: {source_dir}")
        return 1
    if args.min_videos <= 0 or args.max_videos < args.min_videos:
        print("[error] invalid min/max videos settings")
        return 1

    videos = list_videos(source_dir)
    if not videos:
        print(f"[error] no supported videos found in: {source_dir}")
        return 1

    accounts = build_accounts(args.account_prefix, args.account_count, args.password)
    assignments = choose_assignments(
        videos,
        accounts,
        min_videos=args.min_videos,
        max_videos=args.max_videos,
        seed=args.seed,
    )
    client = ApiClient(args.base_url)

    print(f"[info] found {len(videos)} videos")
    for account in accounts:
        token = login_or_register(client, account)
        account_videos = assignments[account.username]
        print(f"[account] {account.username} -> {len(account_videos)} videos")
        for file_path in account_videos:
            try:
                asset_id = upload_video(client, token=token, file_path=file_path)
                content_data = create_content(
                    client,
                    token=token,
                    video_asset_id=asset_id,
                    file_path=file_path,
                    category_id=args.category_id,
                )
                print(
                    f"[content] created id={content_data['id']} "
                    f"title={content_data['title']} by={account.username}"
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[error] failed for {account.username} / {file_path.name}: {exc}")
    print("[done] batch upload finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
