import fs from "node:fs/promises";
import crypto from "node:crypto";
import pathModule from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const args = process.argv.slice(2);
const outputIndex = args.indexOf("--output");
const outputPath = outputIndex >= 0 ? args[outputIndex + 1] : null;
const paths = outputIndex >= 0
  ? args.filter((_, index) => index !== outputIndex && index !== outputIndex + 1)
  : args;
if (paths.length === 0) {
  throw new Error("expected at least one workbook path");
}

const results = [];
for (const path of paths) {
  const bytes = await fs.readFile(path);
  const input = await FileBlob.load(path);
  const workbook = await SpreadsheetFile.importXlsx(input);
  const sheets = [];
  for (let index = 0; ; index += 1) {
    let sheet;
    try {
      sheet = workbook.worksheets.getItemAt(index);
    } catch {
      break;
    }
    if (!sheet) break;
    const usedRange = sheet.getUsedRange(false);
    sheets.push({
      name: sheet.name,
      address: usedRange?.address ?? null,
      values: usedRange?.values ?? [],
    });
  }
  results.push({
    source_file: pathModule.basename(path),
    source_path: pathModule.resolve(path),
    source_sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
    sheets,
  });
}
const payload = `${JSON.stringify(results, null, 2)}\n`;
if (outputPath) {
  await fs.mkdir(pathModule.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, payload, "utf8");
}
console.log(payload);
