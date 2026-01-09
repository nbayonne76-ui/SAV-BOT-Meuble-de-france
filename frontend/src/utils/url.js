const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const getAbsoluteUrl = (rawUrl) => {
  if (!rawUrl) return "";
  const url = String(rawUrl).trim();

  // FIRST: Check if it's already a valid absolute URL (http:// or https://)
  // This must come FIRST to avoid corrupting Cloudinary URLs
  if (/^https?:\/\//i.test(url)) {
    return url;
  }

  // SECOND: Protocol-relative URLs (e.g., //res.cloudinary.com/...)
  if (url.startsWith("//")) {
    console.warn("⚠️ Normalizing protocol-relative URL:", url);
    return `https:${url}`;
  }

  // THIRD: Fix malformed URLs (missing colon: https// instead of https://)
  if (/^https?\/\//i.test(url)) {
    const fixed = url.replace(/^(https?)(\/\/)/i, "$1://");
    console.warn("⚠️ Fixed malformed URL (missing colon):", url, "->", fixed);
    return fixed;
  }

  // FOURTH: Fix missing protocol separator (http/path instead of http://path)
  if (/^https?[^:]/i.test(url) && !url.includes("://")) {
    const fixed = url.replace(/^([a-z]+)(.*)/i, "$1://$2");
    console.warn("⚠️ Fixed malformed URL (missing ://):", url, "->", fixed);
    return fixed;
  }

  // FIFTH: Relative paths starting with '/'
  if (url.startsWith("/")) {
    return `${API_URL}${url}`;
  }

  // LAST: Assume relative resource path
  console.warn("⚠️ Treating as relative path:", url);
  return `${API_URL}/${url}`;
};

export { API_URL };
