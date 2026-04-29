import { apiRequest, ApiError } from "./api";

interface PresignUploadPayload {
  biz_type: string;
  file_name: string;
  file_size: number;
  mime_type: string;
}

interface PresignUploadResponse {
  asset_id: number;
  bucket_name: string;
  object_key: string;
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

async function uploadToPresignedUrl(
  uploadUrl: string,
  headers: Record<string, string>,
  file: File,
) {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    headers,
    body: file,
  });

  if (!response.ok) {
    throw new ApiError("Upload file to MinIO failed.", response.status, response.status);
  }
}

export async function uploadFileToStorage(file: File, bizType: string) {
  const presignPayload: PresignUploadPayload = {
    biz_type: bizType,
    file_name: file.name,
    file_size: file.size,
    mime_type: file.type || "application/octet-stream",
  };

  const presignData = await apiRequest<PresignUploadResponse>("/storage/presign-upload", {
    method: "POST",
    body: JSON.stringify(presignPayload),
  });

  await uploadToPresignedUrl(presignData.upload_url, presignData.headers, file);

  return apiRequest<CompleteUploadResponse>("/storage/complete-upload", {
    method: "POST",
    body: JSON.stringify({ asset_id: presignData.asset_id }),
  });
}

async function uploadChunkToPresignedUrl(
  uploadUrl: string,
  headers: Record<string, string>,
  chunk: Blob,
) {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    headers,
    body: chunk,
  });

  if (!response.ok) {
    throw new ApiError("Upload file chunk to MinIO failed.", response.status, response.status);
  }

  const etag = response.headers.get("etag");
  if (!etag) {
    throw new ApiError("Missing ETag from MinIO chunk upload response.", response.status);
  }

  return etag.replace(/^"+|"+$/g, "");
}

export async function uploadMultipartFileToStorage(
  file: File,
  bizType: string,
  options?: {
    onProgress?: (progress: number) => void;
  },
) {
  const initData = await apiRequest<InitiateMultipartUploadResponse>(
    "/storage/initiate-multipart-upload",
    {
      method: "POST",
      body: JSON.stringify({
        biz_type: bizType,
        file_name: file.name,
        file_size: file.size,
        mime_type: file.type || "application/octet-stream",
      }),
    },
  );

  const parts: Array<{ part_number: number; etag: string }> = [];

  for (let partNumber = 1; partNumber <= initData.part_count; partNumber += 1) {
    const start = (partNumber - 1) * initData.part_size;
    const end = Math.min(start + initData.part_size, file.size);
    const chunk = file.slice(start, end);

    const presignData = await apiRequest<PresignUploadPartResponse>("/storage/presign-upload-part", {
      method: "POST",
      body: JSON.stringify({
        asset_id: initData.asset_id,
        upload_id: initData.upload_id,
        part_number: partNumber,
      }),
    });

    const etag = await uploadChunkToPresignedUrl(
      presignData.upload_url,
      presignData.headers,
      chunk,
    );

    parts.push({
      part_number: partNumber,
      etag,
    });

    options?.onProgress?.(Math.round((partNumber / initData.part_count) * 100));
  }

  return apiRequest<CompleteUploadResponse>("/storage/complete-multipart-upload", {
    method: "POST",
    body: JSON.stringify({
      asset_id: initData.asset_id,
      upload_id: initData.upload_id,
      parts,
    }),
  });
}
