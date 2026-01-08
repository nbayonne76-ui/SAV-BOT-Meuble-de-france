const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const getAbsoluteUrl = (rawUrl) => {
  if (!rawUrl) return "";
  const url = String(rawUrl).trim();

  if (url.startsWith("//")) {
    return `https:${url}`;
  }

  if (/^https?:\/\//i.test(url)) return url;

  if (/^https?\/\//i.test(url)) {
    return url.replace(/^(https?)(\/\/)/i, "$1://");
  }

  if (/^https?/i.test(url) && !url.includes("://")) {
    return url.replace(/^([a-z]+)(.*)/i, "$1://$2");
  }

  if (url.startsWith("/")) return `${API_URL}${url}`;

  return `${API_URL}/${url}`;
};

export { API_URL };
