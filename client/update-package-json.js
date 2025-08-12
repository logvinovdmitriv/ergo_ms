// Скрипт для обновления данных из env файла в package.json файле
import fs from 'fs';
import path from 'path';

// Избегаем импорта vite/rollup на ARM. Берем порт из env либо по умолчанию
const port = process.env.PORT || 8001;

// Путь к файлу package.json
const packageJsonPath = path.resolve(process.cwd(), 'package.json');

// Чтение package.json
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

// Обновление скрипта stop в package.json
packageJson.scripts.stop = `kill-port ${port}`;

// Запись обновленного package.json
fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));