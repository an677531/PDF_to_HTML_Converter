const button = document.getElementById("convert");
const downloadLink = document.getElementById("downloadBundle");
const loadingIndicator = document.getElementById("loadingIndicator");
const loadingText = document.getElementById("loadingText");
const progressContainer = document.getElementById("conversionProgress");
const progressItems = document.getElementById("progressItems");

function updateProgress(fileName, status, message) {
    let progressItem = document.getElementById(`progress-${fileName}`);

    if (!progressItem) {
        progressItem = document.createElement("div");
        progressItem.id = `progress-${fileName}`;
        progressItem.className = "progress-item";
        progressItems.appendChild(progressItem);
    }

    const statusEmoji = {
        'processing': '⟳',
        'success': '✓',
        'error': '✕'
    }[status] || '○';

    progressItem.className = `progress-item ${status}`;
    progressItem.innerHTML = `
        <div class="progress-item-status">${statusEmoji}</div>
        <div>
            <strong>${fileName}</strong><br>
            <small>${message}</small>
        </div>
    `;
}

button.onclick = async () => {

    downloadLink.style.display = "none";
    downloadLink.href = "#";

    const files = document.getElementById("pdf").files;

    if (files.length === 0) {
        alert("Select at least one PDF");
        return;
    }

    loadingIndicator.style.display = "flex";
    progressContainer.style.display = "block";
    progressItems.innerHTML = "";
    button.disabled = true;

    let successCount = 0;
    let errorCount = 0;
    let lastResult = null;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileName = file.name;

        updateProgress(fileName, "processing", "Starting conversion...");

        try {
            const form = new FormData();
            form.append("pdf", file);

            document.getElementById("pdfViewer").src = URL.createObjectURL(file);
            loadingText.textContent = `Processing ${i + 1} of ${files.length}: ${fileName}...`;

            updateProgress(fileName, "processing", "Extracting PDF content...");

            const response = await fetch(
                "/convert",
                {
                    method: "POST",
                    body: form
                }
            );

            if (!response.ok) {
                let errorMessage = "Conversion failed.";

                try {
                    const errorResult = await response.json();
                    if (errorResult.error) {
                        errorMessage = errorResult.error;
                    }
                } catch (parseError) {
                    console.error(parseError);
                }

                throw new Error(errorMessage);
            }

            const result = await response.json();
            lastResult = result;

            document.getElementById("preview").innerHTML = result.html;

            const issuesList = document.getElementById("issues");
            issuesList.innerHTML = "";

            if (result.issues && result.issues.length > 0) {
                result.issues.forEach(issue => {
                    const li = document.createElement("li");
                    li.className = `issue issue-${issue.severity}`;
                    li.innerHTML = `<strong>${issue.severity}:</strong> ${issue.message}`;
                    issuesList.appendChild(li);
                });
            } else {
                const li = document.createElement("li");
                li.textContent = "No accessibility issues found!";
                li.className = "issue issue-success";
                issuesList.appendChild(li);
            }

            successCount++;
            const bundleInfo = result.bundle ? `(${result.bundle.image_count} images)` : "";
            updateProgress(fileName, "success", `Converted successfully ${bundleInfo}`);

            console.log(`Conversion complete for ${fileName}. Issues:`, result.issues);

        } catch (err) {

            errorCount++;
            console.error(`Error converting ${fileName}:`, err);
            updateProgress(fileName, "error", `Error: ${err.message}`);

        }
    }

    loadingIndicator.style.display = "none";
    button.disabled = false;

    const summary = `Completed: ${successCount} successful, ${errorCount} failed`;
    loadingText.textContent = summary;

    if (lastResult && lastResult.bundle && lastResult.bundle.download_url) {
        downloadLink.href = lastResult.bundle.download_url;
        downloadLink.style.display = "inline";
        downloadLink.textContent = `Download last HTML bundle (${lastResult.bundle.image_count} images)`;
    }

    if (errorCount === 0) {
        console.log("All conversions completed successfully!");
    } else if (successCount === 0) {
        alert(`All conversions failed. Check the progress above for details.`);
    }

};