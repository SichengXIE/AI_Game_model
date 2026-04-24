const form = document.querySelector("#generate-form");
const promptInput = document.querySelector("#prompt");
const providerSelect = document.querySelector("#provider-id");
const modelInput = document.querySelector("#model");
const generateButton = document.querySelector("#generate-button");
const statusTitle = document.querySelector("#status-title");
const statusDetail = document.querySelector("#status-detail");
const downloadLink = document.querySelector("#download-link");
const packageId = document.querySelector("#package-id");
const designExplanation = document.querySelector("#design-explanation");
const templateRationale = document.querySelector("#template-rationale");
const assetSpecOutput = document.querySelector("#asset-spec-output");
const packageOutput = document.querySelector("#package-output");

let activeDownloadUrl = null;

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    promptInput.value = button.dataset.prompt;
    promptInput.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await generateAndPackage();
});

loadProviders();

async function loadProviders() {
  try {
    const data = await getJson("/api/providers");
    providerSelect.innerHTML = "";

    data.providers.forEach((provider) => {
      const option = document.createElement("option");
      option.value = provider.id;
      option.textContent = `${provider.display_name} (${provider.id})`;
      option.dataset.defaultModel = provider.default_model;
      providerSelect.append(option);
    });

    providerSelect.value = data.default_provider_id;
    syncDefaultModel();
    setStatus("等待输入", "模型提供商已载入。后端需要配置对应 API Key 环境变量。");
  } catch (error) {
    setStatus("后端未连接", `无法读取 /api/providers：${error.message}`);
  }
}

providerSelect.addEventListener("change", syncDefaultModel);

function syncDefaultModel() {
  const selected = providerSelect.selectedOptions[0];
  if (selected?.dataset.defaultModel) {
    modelInput.value = selected.dataset.defaultModel;
  }
}

async function generateAndPackage() {
  resetDownload();
  setBusy(true);
  renderJson(assetSpecOutput, {});
  renderJson(packageOutput, {});
  templateRationale.innerHTML = "<li>正在等待 AI 生成模板选择理由。</li>";
  designExplanation.textContent = "正在生成 Asset Spec。";

  try {
    const prompt = promptInput.value.trim();
    setStatus("生成中", "正在调用 /api/specs/generate，把自然语言转成 Asset Spec。");

    const specResult = await postJson("/api/specs/generate", {
      provider_id: providerSelect.value,
      model: modelInput.value.trim(),
      prompt,
      user_constraints: {
        include_assembly: true,
        target_runtime: "cs2_base_mod",
        output_package: true,
      },
    });

    renderSpecResult(specResult);

    if (specResult.status === "needs_clarification") {
      setStatus("需要补充信息", "AI 需要更多约束后才能生成可打包资产。");
      return;
    }

    if (specResult.status !== "ready" || !specResult.asset_spec) {
      setStatus("生成未通过", "Asset Spec 没有达到可打包状态，请检查验证问题。");
      return;
    }

    setStatus("打包中", "正在调用 /api/packages/build，生成 Base Mod 可读取的 zip 包。");
    const packageResult = await postJson("/api/packages/build", {
      asset_spec: specResult.asset_spec,
    });

    renderJson(packageOutput, packageResult);

    if (packageResult.status !== "ready") {
      setStatus("打包失败", packageResult.error?.message || "Package Builder 返回了无效状态。");
      return;
    }

    attachDownload(packageResult);
    setStatus("可以下载", "资产包已生成。把包内 active-asset.json 交给 CS2 Base Mod 读取。");
  } catch (error) {
    setStatus("流程中断", error.message);
  } finally {
    setBusy(false);
  }
}

function renderSpecResult(result) {
  designExplanation.textContent = result.design_explanation || "没有设计说明。";
  renderJson(assetSpecOutput, result.asset_spec || result);

  templateRationale.innerHTML = "";
  const rationale = result.template_rationale?.length
    ? result.template_rationale
    : result.questions?.map((question) => question.question) || result.validation_issues?.map((issue) => issue.message);

  (rationale?.length ? rationale : ["没有返回模板选择理由。"]).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    templateRationale.append(li);
  });
}

function attachDownload(packageResult) {
  const blob = base64ToBlob(packageResult.zip_base64, packageResult.content_type || "application/zip");
  activeDownloadUrl = URL.createObjectURL(blob);
  downloadLink.href = activeDownloadUrl;
  downloadLink.download = packageResult.filename;
  downloadLink.classList.remove("disabled");
  downloadLink.setAttribute("aria-disabled", "false");
  packageId.textContent = packageResult.package_id;
}

function resetDownload() {
  if (activeDownloadUrl) {
    URL.revokeObjectURL(activeDownloadUrl);
    activeDownloadUrl = null;
  }
  downloadLink.href = "#";
  downloadLink.removeAttribute("download");
  downloadLink.classList.add("disabled");
  downloadLink.setAttribute("aria-disabled", "true");
  packageId.textContent = "尚未生成";
}

function base64ToBlob(base64, contentType) {
  const binary = atob(base64);
  const chunks = [];

  for (let offset = 0; offset < binary.length; offset += 1024) {
    const slice = binary.slice(offset, offset + 1024);
    const bytes = new Uint8Array(slice.length);
    for (let index = 0; index < slice.length; index += 1) {
      bytes[index] = slice.charCodeAt(index);
    }
    chunks.push(bytes);
  }

  return new Blob(chunks, { type: contentType });
}

async function getJson(url) {
  const response = await fetch(url);
  return readJsonResponse(response);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return readJsonResponse(response);
}

async function readJsonResponse(response) {
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const message = data.error?.message || `${response.status} ${response.statusText}`;
    throw new Error(message);
  }

  return data;
}

function setBusy(isBusy) {
  generateButton.disabled = isBusy;
  generateButton.textContent = isBusy ? "正在生成..." : "生成 Asset Spec 并打包";
}

function setStatus(title, detail) {
  statusTitle.textContent = title;
  statusDetail.textContent = detail;
}

function renderJson(target, value) {
  target.textContent = JSON.stringify(value, null, 2);
}
