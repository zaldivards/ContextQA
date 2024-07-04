export function formatCode(message) {
    const formattedText = message.replaceAll('<code>', "<code class='text-yellow-600 bg-black-alpha-70 w-min'>")
    return formattedText.replaceAll("`", "").replaceAll("\\n", '<br>').replaceAll(
        "ContextQA",
        `<span class="relative"
            ><img
              alt="contextqa text"
              src="/images/title.png"
              class="top-img relative"
              width='80'
          /></span>`
    );
}
