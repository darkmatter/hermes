#!/usr/bin/env bun
/**
 * One-shot port helper used by the RedwoodSDK migration prototype.
 * Strips Next.js App Router specifics (metadata, generateStaticParams, etc.)
 * from a file copied from app/**\/page.tsx and renames its default export.
 *
 * Usage: bun scripts/port-page.ts <file> <ExportName>
 */
import { readFile, writeFile } from "node:fs/promises";

const [, , filePath, exportName] = process.argv;
if (!filePath || !exportName) {
  console.error("usage: port-page.ts <file> <ExportName>");
  process.exit(1);
}

let src = await readFile(filePath, "utf8");

function findMatchingBrace(input: string, openIdx: number): number {
  if (input[openIdx] !== "{") return -1;
  let depth = 0;
  for (let i = openIdx; i < input.length; i++) {
    const ch = input[i];
    if (ch === "{") depth++;
    else if (ch === "}") {
      depth--;
      if (depth === 0) return i;
    }
  }
  return -1;
}

/** Remove an `export const NAME = { ... };` declaration. */
function stripExportConstObject(input: string, name: string): string {
  const re = new RegExp(
    `export\\s+const\\s+${name}(?:\\s*:\\s*[^=]+)?\\s*=\\s*`,
    "g",
  );
  let m: RegExpExecArray | null;
  while ((m = re.exec(input))) {
    const openIdx = input.indexOf("{", m.index + m[0].length - 1);
    if (openIdx === -1) break;
    const closeIdx = findMatchingBrace(input, openIdx);
    if (closeIdx === -1) break;
    let end = closeIdx + 1;
    while (input[end] === ";" || input[end] === "\n") end++;
    input = input.slice(0, m.index) + input.slice(end);
    re.lastIndex = 0;
  }
  return input;
}

/** Remove an `export async? function NAME(...) { ... }` declaration. */
function stripExportFunction(input: string, name: string): string {
  const re = new RegExp(
    `export\\s+(?:async\\s+)?function\\s+${name}\\s*\\(`,
    "g",
  );
  let m: RegExpExecArray | null;
  while ((m = re.exec(input))) {
    let i = m.index + m[0].length - 1;
    let depth = 0;
    for (; i < input.length; i++) {
      const ch = input[i];
      if (ch === "(") depth++;
      else if (ch === ")") {
        depth--;
        if (depth === 0) {
          i++;
          break;
        }
      }
    }
    while (i < input.length && input[i] !== "{") i++;
    if (input[i] !== "{") break;
    const closeIdx = findMatchingBrace(input, i);
    if (closeIdx === -1) break;
    let end = closeIdx + 1;
    while (input[end] === "\n") end++;
    input = input.slice(0, m.index) + input.slice(end);
    re.lastIndex = 0;
  }
  return input;
}

// 1. Remove `import type { Metadata } from "next";`
src = src.replace(
  /^import\s+type\s+\{\s*Metadata\s*\}\s+from\s+["']next["'];?\s*\n/gm,
  "",
);

// 2. `export const metadata = {...};` (with or without type annotation)
src = stripExportConstObject(src, "metadata");

// 3. `export async function generateMetadata(...) { ... }`
src = stripExportFunction(src, "generateMetadata");

// 4. `export async function generateStaticParams() { ... }`
src = stripExportFunction(src, "generateStaticParams");

// 6. Remove single-line export consts: dynamic, runtime, revalidate, fetchCache, etc.
src = src.replace(
  /^export\s+const\s+(?:dynamic|runtime|revalidate|fetchCache|dynamicParams|preferredRegion|maxDuration|contentType|alt|size)\s*[:=][^;\n]*;?\s*\n/gm,
  "",
);

// 7. `params: Promise<{...}>` -> `params: {...}`
src = src.replace(/params\s*:\s*Promise<\s*(\{[^}]*\})\s*>/g, "params: $1");

// 8. `const { ... } = await params;` -> `const { ... } = params;`
src = src.replace(/=\s*await\s+params\b/g, "= params");

// 9. Default export -> named export
src = src.replace(
  /export\s+default\s+async\s+function\s+\w+/,
  `export async function ${exportName}`,
);
src = src.replace(
  /export\s+default\s+function\s+\w+/,
  `export function ${exportName}`,
);

// 10. Collapse multiple blank lines
src = src.replace(/\n{3,}/g, "\n\n");

await writeFile(filePath, src);
console.log(`ported ${filePath} -> ${exportName}`);
