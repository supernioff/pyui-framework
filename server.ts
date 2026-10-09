import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);
const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;
const IS_PROD = process.env.NODE_ENV === 'production';
const ROOT_DIR = process.cwd();
const PYUI_DIR = path.join(ROOT_DIR, 'pyui');

app.use(express.json());

// -----------------------------------------------------------------------------
// Python Execution Helper
// -----------------------------------------------------------------------------
async function runPythonBridge(args: string[]): Promise<any> {
  const runnerScript = path.join(PYUI_DIR, 'runner_bridge.py');
  try {
    const { stdout } = await execFileAsync('python3', [runnerScript, ...args], {
      cwd: PYUI_DIR,
      timeout: 10000,
    });
    return JSON.parse(stdout.trim());
  } catch (error: any) {
    console.error('Python bridge error:', error);
    return {
      error: error.message || 'Python execution failed',
      stderr: error.stderr || '',
      stdout: error.stdout || '',
    };
  }
}

// -----------------------------------------------------------------------------
// PyUI API Endpoints
// -----------------------------------------------------------------------------

// 1. Render initial UI from Python
app.get('/api/pyui/render', async (req, res) => {
  const appType = (req.query.app as string) || 'quiz';
  const result = await runPythonBridge(['render', appType]);
  res.json(result);
});

// 2. Dispatch event to Python and return new rendered HTML
app.post('/api/pyui/dispatch', async (req, res) => {
  const { app: appType = 'quiz', id = '', event = 'click', state = {} } = req.body;
  const stateStr = JSON.stringify(state);
  const result = await runPythonBridge(['dispatch', appType, id, event, stateStr]);
  res.json(result);
});

// 3. Run automated Python unit test suite
app.get('/api/pyui/test', async (req, res) => {
  const result = await runPythonBridge(['test']);
  res.json(result);
});

// 4. Retrieve all project source code files for explorer & download
app.get('/api/pyui/files', (req, res) => {
  try {
    const files = [
      { name: 'framework.py', path: 'framework.py', category: 'core' },
      { name: 'app.py', path: 'app.py', category: 'app' },
      { name: 'counter_app.py', path: 'counter_app.py', category: 'app' },
      { name: 'test_framework.py', path: 'test_framework.py', category: 'test' },
      { name: 'static/style.css', path: 'static/style.css', category: 'static' },
      { name: 'static/client.js', path: 'static/client.js', category: 'static' },
      { name: 'requirements.txt', path: 'requirements.txt', category: 'meta' },
      { name: 'README.md', path: 'README.md', category: 'docs' },
    ];

    const fileContents = files.map((f) => {
      const fullPath = path.join(PYUI_DIR, f.path);
      const content = fs.existsSync(fullPath) ? fs.readFileSync(fullPath, 'utf-8') : '';
      return {
        name: f.name,
        category: f.category,
        content,
      };
    });

    res.json({ success: true, files: fileContents });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 5. Serve PyUI static assets if requested directly
app.use('/pyui/static', express.static(path.join(PYUI_DIR, 'static')));

// -----------------------------------------------------------------------------
// Vite Middleware / Static Serving
// -----------------------------------------------------------------------------
async function startServer() {
  if (!IS_PROD) {
    const vite = await createViteServer({
      server: { middlewareMode: true, port: PORT },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(ROOT_DIR, 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server listening on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
