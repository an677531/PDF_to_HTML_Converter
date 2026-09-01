/*
===========================================================
ACCESSIBLE NEWS AI CONVERTER PROJECT NOTES
===========================================================

CURRENT STATUS:
Frontend prototype completed.

Implemented:
- PDF file selection
- Local PDF preview
- FormData upload preparation

CURRENTLY STOPPED BEFORE:
Python backend implementation.

NEXT DEVELOPMENT PHASE:
Build Flask/Python backend responsible for:

1. Receiving uploaded PDFs
2. Extracting:
   - article text
   - images
   - captions
   - layout information

3. Creating structured document JSON

4. Connecting to Ollama:
   - article semantic formatter
   - image accessibility agent
   - accessibility reviewer

5. Returning:
   {
      html: generated accessible article,
      issues: review findings
   }

The frontend only:
UPLOAD -> REQUEST -> DISPLAY RESULTS

===========================================================
*/
const button = document.getElementById("convert");
const downloadLink = document.getElementById("downloadBundle");
const loadingIndicator = document.getElementById("loadingIndicator");
const loadingText = document.getElementById("loadingText");
const progressContainer = document.getElementById("conversionProgress");
const progressItems = document.getElementById("progressItems");

// Helper function to add/update progress item
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

    // Show loading indicator and progress
    loadingIndicator.style.display = "flex";
    progressContainer.style.display = "block";
    progressItems.innerHTML = "";
    button.disabled = true;

    let successCount = 0;
    let errorCount = 0;
    let lastResult = null;

    // Process each file sequentially
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileName = file.name;

        updateProgress(fileName, "processing", "Starting conversion...");

        try {
            const form = new FormData();
            form.append("pdf", file);

            // Show PDF in viewer for current file
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

            // Display preview and issues for the currently processed file
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

    // Hide loading indicator
    loadingIndicator.style.display = "none";
    button.disabled = false;

    // Show completion summary
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