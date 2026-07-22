import { marked } from 'marked'

marked.setOptions({
  breaks: true,
  gfm: true,
})

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/<[^>]*>/g, '')      // strip HTML tags
    .replace(/[^\w一-鿿]+/g, '-')  // replace non-word/non-CJK with dash
    .replace(/^-+|-+$/g, '')       // trim dashes
}

export function renderMarkdown(text) {
  if (!text) return ''
  let html = marked.parse(text)
  // Inject heading IDs so outline links can anchor to them
  html = html.replace(/<(h[1-4])>(.*?)<\/\1>/gi, (_, tag, content) => {
    const id = slugify(content)
    return `<${tag} id="${id}">${content}</${tag}>`
  })
  return html
}

export function extractOutline(text) {
  if (!text) return []
  const headingRegex = /^(#{1,4})\s+(.+)$/gm
  const outline = []
  let match
  while ((match = headingRegex.exec(text)) !== null) {
    const headingText = match[2].trim()
    outline.push({
      level: match[1].length,
      text: headingText,
      id: slugify(headingText),
    })
  }
  return outline
}
