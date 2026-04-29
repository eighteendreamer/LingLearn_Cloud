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
