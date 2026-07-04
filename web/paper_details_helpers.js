(function exposePaperDetailsHelpers(root, factory) {
  const helpers = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = helpers;
  }
  root.PaperDetailsHelpers = helpers;
}(typeof globalThis !== "undefined" ? globalThis : this, function buildHelpers() {
  function canonicalNameTokens(value) {
    const displayName = String(
      value && typeof value === "object"
        ? value.name || value.author || ""
        : value || "",
    ).trim();
    const commaParts = displayName.split(",");
    const orderedName = commaParts.length === 2
      ? `${commaParts[1].trim()} ${commaParts[0].trim()}`
      : displayName;
    return orderedName
      .normalize("NFKD")
      .replace(/\p{M}/gu, "")
      .toLocaleLowerCase()
      .match(/[\p{L}\p{N}]+/gu) || [];
  }

  function namesMatch(left, right) {
    const leftTokens = canonicalNameTokens(left);
    const rightTokens = canonicalNameTokens(right);
    if (!leftTokens.length || leftTokens.length !== rightTokens.length) {
      return false;
    }
    if (leftTokens.every((token, index) => token === rightTokens[index])) {
      return true;
    }
    const sortedLeft = [...leftTokens].sort();
    const sortedRight = [...rightTokens].sort();
    if (sortedLeft.every((token, index) => token === sortedRight[index])) {
      return true;
    }
    if (leftTokens.length < 3) {
      return false;
    }
    const tokenMatches = (leftToken, rightToken) => (
      leftToken === rightToken
      || (
        Math.min(leftToken.length, rightToken.length) === 1
        && leftToken[0] === rightToken[0]
      )
    );
    return leftTokens.every((token, index) => tokenMatches(token, rightTokens[index]))
      || leftTokens.every((token, index) => (
        tokenMatches(token, rightTokens[rightTokens.length - index - 1])
      ));
  }

  function renderPaperAuthors(paper, escapeHtml, currentAffiliationNumber = null) {
    const authors = Array.isArray(paper?.authors) ? paper.authors : [];
    return authors.map((author) => {
      const numbers = Array.isArray(author.affiliation_indices)
        ? author.affiliation_indices
        : [];
      const superscript = numbers.length
        ? `<sup class="author-affiliation-numbers" aria-label="Affiliations ${numbers.join(", ")}">${numbers.join(",")}</sup>`
        : "";
      const isActive = author.is_current_marker_author === true || (
        currentAffiliationNumber !== null
        && numbers.includes(currentAffiliationNumber)
      );
      const authorHtml = `<span class="paper-author${isActive ? " is-active-institution-author is-hover-author" : ""}">${escapeHtml(author.name)}${superscript}</span>`;
      return isActive
        ? `<strong class="current-institution-author">${authorHtml}</strong>`
        : authorHtml;
    }).join(", ");
  }

  return { namesMatch, renderPaperAuthors };
}));
