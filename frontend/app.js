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

button.onclick = async () => {

    downloadLink.style.display = "none";
    downloadLink.href = "#";

    const file = document.getElementById("pdf").files[0];

    if (!file) {
        alert("Select PDF");
        return;
    }

    const form = new FormData();
    form.append("pdf", file);

    document.getElementById("pdfViewer").src =
        URL.createObjectURL(file);

    try {

        // Show loading state
        document.getElementById("preview").textContent = "Converting PDF...";
        document.getElementById("issues").innerHTML = "";

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

        document.getElementById("preview").innerHTML = result.html;

        if (result.bundle && result.bundle.download_url) {
            downloadLink.href = result.bundle.download_url;
            downloadLink.style.display = "inline";
            downloadLink.textContent = `Download HTML bundle (${result.bundle.image_count} images)`;
        }

        // Display issues
        const issuesList = document.getElementById("issues");
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

        console.log("Conversion complete. Issues:", result.issues);

    } catch (err) {

        console.error(err);

        document.getElementById("preview").textContent = "Error: " + err.message;
        document.getElementById("issues").innerHTML = "";

        alert("Unable to convert PDF: " + err.message);

    }

};