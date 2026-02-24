const sourceFileEl = document.getElementById("sourceFile");
const sourceFolderEl = document.getElementById("sourceFolder");
const outputDirEl = document.getElementById("outputDir");
const heightEl = document.getElementById("height");
const crfEl = document.getElementById("crf");
const presetEl = document.getElementById("preset");
const audioBitrateEl = document.getElementById("audioBitrate");
const startBtn = document.getElementById("startBtn");

const statusTextEl = document.getElementById("statusText");
const currentFileEl = document.getElementById("currentFile");
const progressTextEl = document.getElementById("progressText");
const progressBarEl = document.getElementById("progressBar");

let activeJobId = null;
let timerId = null;

function showError(message) {
  statusTextEl.textContent = `错误: ${message}`;
}

async function postJson(url, payload) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(data.detail || "请求失败");
  }
  return data;
}

function updateProgress(value) {
  const percentage = Math.max(0, Math.min(100, Math.round(value * 100)));
  progressTextEl.textContent = `${percentage}%`;
  progressBarEl.style.width = `${percentage}%`;
}

function setRunningState(running) {
  startBtn.disabled = running;
  document.getElementById("pickFileBtn").disabled = running;
  document.getElementById("pickFolderBtn").disabled = running;
  document.getElementById("pickOutputBtn").disabled = running;
}

async function pickPath(kind, targetEl) {
  try {
    const result = await postJson("/api/pick-path", { kind });
    if (result.path) {
      targetEl.value = result.path;
      if (targetEl === sourceFileEl) {
        sourceFolderEl.value = "";
      }
      if (targetEl === sourceFolderEl) {
        sourceFileEl.value = "";
      }
    }
  } catch (err) {
    showError(err.message);
  }
}

async function pollJob() {
  if (!activeJobId) {
    return;
  }
  try {
    const resp = await fetch(`/api/jobs/${activeJobId}`);
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || "查询任务失败");
    }

    statusTextEl.textContent = data.message || data.status;
    currentFileEl.textContent = data.current_file || "-";
    updateProgress(data.progress || 0);

    if (data.status === "completed") {
      setRunningState(false);
      statusTextEl.textContent = "转换完成";
      clearInterval(timerId);
      timerId = null;
    } else if (data.status === "failed") {
      setRunningState(false);
      statusTextEl.textContent = `转换失败: ${data.error || "未知错误"}`;
      clearInterval(timerId);
      timerId = null;
    }
  } catch (err) {
    setRunningState(false);
    clearInterval(timerId);
    timerId = null;
    showError(err.message);
  }
}

document.getElementById("pickFileBtn").addEventListener("click", async () => {
  await pickPath("source_file", sourceFileEl);
});

document.getElementById("pickFolderBtn").addEventListener("click", async () => {
  await pickPath("source_folder", sourceFolderEl);
});

document.getElementById("pickOutputBtn").addEventListener("click", async () => {
  await pickPath("output_folder", outputDirEl);
});

startBtn.addEventListener("click", async () => {
  const sourcePath = sourceFileEl.value || sourceFolderEl.value;
  const outputDir = outputDirEl.value;

  if (!sourcePath) {
    showError("请先选择输入文件或输入文件夹");
    return;
  }
  if (!outputDir) {
    showError("请先选择输出目录");
    return;
  }

  try {
    setRunningState(true);
    statusTextEl.textContent = "正在创建任务";
    updateProgress(0);
    currentFileEl.textContent = "-";

    const payload = {
      source_path: sourcePath,
      output_dir: outputDir,
      height: Number(heightEl.value),
      crf: Number(crfEl.value),
      preset: presetEl.value,
      audio_bitrate: audioBitrateEl.value,
    };

    const job = await postJson("/api/start", payload);
    activeJobId = job.job_id;
    statusTextEl.textContent = "任务已启动";
    if (timerId) {
      clearInterval(timerId);
    }
    timerId = setInterval(pollJob, 800);
    await pollJob();
  } catch (err) {
    setRunningState(false);
    showError(err.message);
  }
});
