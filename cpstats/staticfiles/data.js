document.addEventListener("DOMContentLoaded", () => {
  const cards = [
    {
      inputId: "cf-input",
      fetchId: "cf-fetch",
      resetId: "cf-reset",
      cardId: "cf",
      url: "/cf_ajax/",
      profileUrl: "https://codeforces.com/profile/",
    },
    {
      inputId: "lc-input",
      fetchId: "lc-fetch",
      resetId: "lc-reset",
      cardId: "lc",
      url: "/lc_ajax/",
      profileUrl: "https://leetcode.com/",
    },
    {
      inputId: "cc-input",
      fetchId: "cc-fetch",
      resetId: "cc-reset",
      cardId: "cc",
      url: "/cc_ajax/",
      profileUrl: "https://www.codechef.com/users/",
    },
    {
      inputId: "at-input",
      fetchId: "at-fetch",
      resetId: "at-reset",
      cardId: "at",
      url: "/at_ajax/",
      profileUrl: "https://atcoder.jp/users/",
    },
  ];

  cards.forEach((card) => {
    const cardDiv = document.getElementById(card.cardId);
    const input = document.getElementById(card.inputId);
    const fetchBtn = document.getElementById(card.fetchId);

    // Save original inner HTML (logo + input + fetch)
    const originalContent = cardDiv.innerHTML;

    fetchBtn.addEventListener("click", () => {
      const username = input.value.trim();
      if (!username) return alert("Enter a username");

      const param = card.url.includes("at") ? "username" : "handle";

      fetch(`${card.url}?${param}=${username}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.error) {
            cardDiv.innerHTML = `<p class="text-red-500">${data.error}</p>`;
          } else {
            const logoHtml = cardDiv.querySelector("img")?.outerHTML || "";

            let html = `${logoHtml}<div class="mt-4">`;
            html += `<h2 class="text-lg font-bold mb-2">
            <a href="${card.profileUrl}${username}" target="_blank" 
               class="text-yellow-300 hover:underline">
               ${username}
            </a>
         </h2>`;

            html += '<div class="text-left text-amber-950">';
            for (const key in data) {
              if (key.toLowerCase() === "username") continue;
              html += `<p><strong>${key.replace(/_/g, " ")}:</strong> ${
                data[key]
              }</p>`;
            }
            html += "</div>";
            html += `<button id="${card.resetId}" class="mt-4 hover:bg-gray-400 p-1 transition">Reset</button>`;
            html += "</div>";

            cardDiv.innerHTML = html;

            const newResetBtn = document.getElementById(card.resetId);
            newResetBtn.addEventListener("click", () => {
              cardDiv.innerHTML = originalContent;
            });
          }
        });
    });
  });
});
