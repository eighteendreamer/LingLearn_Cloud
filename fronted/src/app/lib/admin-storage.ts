import { adminApiRequest, ApiError } from "./api";

interface InitiateMultipartUploadResponse {
  asset_id: number;
  bucket_name: string;
  object_key: string;
  upload_id: string;
  part_size: number;
  part_count: number;
}

interface PresignUploadPartResponse {
  asset_id: number;
  upload_id: string;
  part_number: number;
  upload_url: string;
  headers: Record<string, string>;
}

interface CompleteUploadResponse {
  asset_id: number;
  bucket_name: string;
  object_key: string;
  status: string;
  file_size: number;
  mime_type: string;
  public_url: string | null;
}

async function uploadChunk(url: string, headers: Record<string, string>, chunk: Blob) {
  const response = await fetch(url, { method: "PUT", headers, body: chunk });
  if (!response.ok) {
    throw new ApiError("Upload chunk failed.", response.status);
  }
  const etag = response.headers.get("etag");
  if (!etag) {
    throw new ApiError("Missing ETag.", response.status);
  }
  return etag.replace(/^"+|"+$/g, "");
}

export async function adminUploadVideo(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<CompleteUploadResponse> {
  const initData = await adminApiRequest<InitiateMultipartUploadResponse>(
    "/admin/management/storage/initiate-multipart-upload",
    {
      method: "POST",
      body: JSON.stringify({
        biz_type: "content_video",
        file_name: file.name,
        file_size: file.size,
        mime_type: file.type || "video/mp4",
      }),
    },
  );

  const parts: Array<{ part_number: number; etag: string }> = [];

  for (let partNumber = 1; partNumber <= initData.part_count; partNumber += 1) {
    const start = (partNumber - 1) * initData.part_size;
    const end = Math.min(start + initData.part_size, file.size);
    const chunk = file.slice(start, end);

    const presignData = await adminApiRequest<PresignUploadPartResponse>(
      "/admin/management/storage/presign-upload-part",
      {
        method: "POST",
        body: JSON.stringify({
          asset_id: initData.asset_id,
          upload_id: initData.upload_id,
          part_number: partNumber,
        }),
      },
    );

    const etag = await uploadChunk(presignData.upload_url, presignData.headers, chunk);
    parts.push({ part_number: partNumber, etag });
    onProgress?.(Math.round((partNumber / initData.part_count) * 100));
  }

  return adminApiRequest<CompleteUploadResponse>(
    "/admin/management/storage/complete-multipart-upload",
    {
      method: "POST",
      body: JSON.stringify({
        asset_id: initData.asset_id,
        upload_id: initData.upload_id,
        parts,
      }),
    },
  );
}

export async function adminCreateContentItem(data: {
  title: string;
  primary_media_asset_id: number;
  content_type?: string;
  category_id?: number | null;
}): Promise<{ id: number; title: string }> {
  return adminApiRequest("/admin/management/content-items", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function adminUploadCover(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<CompleteUploadResponse> {
  const presignData = await adminApiRequest<{
    asset_id: number;
    upload_url: string;
    headers: Record<string, string>;
  }>("/admin/management/storage/presign-upload", {
    method: "POST",
    body: JSON.stringify({
      biz_type: "content_cover",
      file_name: file.name,
      file_size: file.size,
      mime_type: file.type || "image/jpeg",
    }),
  });

  onProgress?.(30);

  const putResponse = await fetch(presignData.upload_url, {
    method: "PUT",
    headers: presignData.headers,
    body: file,
  });
  if (!putResponse.ok) {
    throw new ApiError("Cover upload failed.", putResponse.status);
  }

  onProgress?.(70);

  const result = await adminApiRequest<CompleteUploadResponse>(
    "/admin/management/storage/complete-upload",
    {
      method: "POST",
      body: JSON.stringify({ asset_id: presignData.asset_id }),
    },
  );

  onProgress?.(100);
  return result;
}
