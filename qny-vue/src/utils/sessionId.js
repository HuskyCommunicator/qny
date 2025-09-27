// 会话ID生成工具
export async function generateSessionId(userId, roleId) {
  const raw = `${userId}_${roleId}`;
  const buffer = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(raw)
  );
  const hashArr = Array.from(new Uint8Array(buffer));
  return hashArr
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .slice(0, 8);
}
