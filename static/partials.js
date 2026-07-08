/* Shared nav + footer for all PhishWatch pages.
   Each page sets <body data-page="home|scan|monitoring|pricing|about">. */
(function(){
  const page = document.body.getAttribute("data-page") || "";
  const link = (href,label,key)=>
    `<a href="${href}" class="${key===page?'active':''}">${label}</a>`;

  const nav = `
    <nav><div class="wrap nav-inner">
      <a href="/" class="brand"><span class="dot"></span>PhishWatch</a>
      <div class="nav-links" id="navLinks">
        ${link("/","Home","home")}
        ${link("/scan.html","Scan","scan")}
        ${link("/monitoring.html","Monitoring","monitoring")}
        ${link("/pricing.html","Pricing","pricing")}
        ${link("/about.html","About","about")}
      </div>
      <a href="/scan.html" class="nav-cta">Run a scan</a>
      <button class="nav-toggle" id="navToggle" aria-label="Menu">&#9776;</button>
    </div></nav>`;

  const footer = `
    <footer><div class="wrap">
      <div class="foot-grid">
        <div class="foot-col">
          <a href="/" class="brand"><span class="dot"></span>PhishWatch</a>
          <p class="foot-about">Real-time detection of lookalike domains and brand impersonation, built on public Certificate Transparency logs.</p>
        </div>
        <div class="foot-col">
          <h5>Product</h5>
          <a href="/scan.html">One-time scan</a>
          <a href="/monitoring.html">Continuous monitoring</a>
          <a href="/pricing.html">Pricing</a>
        </div>
        <div class="foot-col">
          <h5>Company</h5>
          <a href="/about.html">About</a>
          <a href="https://github.com/ShahzaibNas/phishwatch" target="_blank" rel="noopener">GitHub</a>
        </div>
      </div>
      <div class="foot-bottom">
        <span>&copy; ${new Date().getFullYear()} PhishWatch</span>
        <span>Built for teams who can't afford to be impersonated.</span>
      </div>
    </div></footer>`;

  document.body.insertAdjacentHTML("afterbegin", nav);
  document.body.insertAdjacentHTML("beforeend", footer);

  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if(toggle) toggle.addEventListener("click", ()=>links.classList.toggle("open"));
})();