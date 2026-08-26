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

button.onclick = async () => {

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

        const response = await fetch(
            "http://localhost:5001/convert",
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

        console.log(result.issues);

    } catch (err) {

        console.error(err);

        document.getElementById("preview").textContent = err.message;

        alert("Unable to convert PDF.");

    }

};