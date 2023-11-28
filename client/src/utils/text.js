export function formatCode(message) {
    const formattedText = message
        .replaceAll(
            /(?<=```)(?!<br>{2}|\s+\-)([\s\S]+?)?(?=```)/g,
            (match, offset, text) => {
                const lines = match.split("<br>");
                if (lines.length > 1 && /[\w\s]/.test(lines[0].at(-1))) {
                    match = lines.slice(1).join("<br>");
                }
                return `<code class='text-yellow-600 bg-black-alpha-70 p-3 w-auto block'>${match.trim()}</code>`;
            }
        )
        .replaceAll("```", "")
        .replaceAll(/(?<=`)(?![\s.,)])[^`]+(?=`)/g, (match, offset, text) => {
            return `<code class='text-yellow-600 bg-black-alpha-70 p-1 w-min'>${match}</code>`;
        })
        .replaceAll(/\[.+\]\([\w:\/.\-]+\)/g, (match, offset, text) => {
            const parts = match.match(/\[(.*?)\]\((.*?)\)/, "$1");
            return `<a href="${parts[2]}">${parts[1]}</a>`;
        });
    return formattedText.replaceAll("`", "").replaceAll(
        "ContextQA",
        `<span class="relative"
            ><img
              alt="contextqa text"
              src="/images/title.png"
              class="w-1 top-img relative"
          /></span>`
    );
}

export function clean(token, escaped) {
    return token.replaceAll(/\\n|\n/g, "<br>").replaceAll(/ {3}/g, "&nbsp;&nbsp;&nbsp;");
}